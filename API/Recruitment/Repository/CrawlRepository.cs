using Amazon.Auth.AccessControlPolicy;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using MongoDB.Bson;
using MongoDB.Bson.IO;
using MongoDB.Driver;
using MoreLinq;
using Recruitment.Common;
using Recruitment.Extensions;
using Recruitment.Model;
using Recruitment.Model.CrawlModel;
using Recruitment.Model.Response;
using Recruitment.Repository.Entities;
using Recruitment.Wapper;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Recruitment.Repository
{
    public class CrawlRepository : ICrawlRepository
    {
        private readonly IMongoCollection<Job> _collectionJob;
        private readonly IMongoCollection<Job_Error> _collectionJob_Error;
        private readonly DbConfiguration _settings;
        private readonly ILogger<CrawlRepository> _logger;
        public CrawlRepository(IOptions<DbConfiguration> settings, ILogger<CrawlRepository> logger)
        {
            _settings = settings.Value;
            var client = new MongoClient(_settings.ConnectionString);
            var database = client.GetDatabase(_settings.DatabaseName);
            _collectionJob = database.GetCollection<Job>(_settings.CollectionJob);
            _collectionJob_Error = database.GetCollection<Job_Error>(_settings.CollectionJobError);
            _logger = logger;
        }

        public async Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string idError, string source, DateTime from, DateTime to)
        {
            _logger.LogInformation($"GetErrorByWebsiteDateAsync: idError{idError} - website:{source} - from:{from.ToString("dd/MM/yyyy")} - to:{to.ToString("dd/MM/yyyy")}  ");
            try
            {
                var listJobError = new List<Job_Error>();


                if (string.IsNullOrEmpty(source))
                {
                    listJobError = await _collectionJob_Error.Find(x => x.created_date >= from && x.created_date <= to).ToListAsync();
                }
                else
                {
                    listJobError = await _collectionJob_Error.Find(x => x.created_date >= from && x.created_date <= to && x.source == source).ToListAsync();
                }

                if (!string.IsNullOrEmpty(idError))
                {
                    listJobError = listJobError.Where(x => x.id_error == idError).ToList();
                }

                listJobError = listJobError.OrderByDescending(x => x.created_date).ToList();

                var result = listJobError?.Select(x => new JobErrorResponse()
                {
                    IdRrror = x?.id_error,
                    Source = x?.source,
                    CreatedDate = x?.created_date_string,
                    ErrorMessage = x?.error_message,
                    TimeCrawl = x?.created_date.ToString("dd/MM/yyy HH:mm:ss")
                }).ToList();

                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error GetErrorByWebsiteDateAsync - Message: {ex.Message}  ");
                return new List<JobErrorResponse>();
            }


        }

        public async Task<PaginatedList<DataListJob>> GetJobByDateAsync(DateTime from, DateTime to, int pageIndex, int pageSize)
        {
            try
            {
                var listError = new List<Job_Error>();
                var listJobByDateResult = new List<GetJobByDateResult>();
                var jobByDateResponse = new GetJobByDateResponse();
                listError = await _collectionJob_Error.Find(x => x.created_date >= from && x.created_date <= to).ToListAsync();

                // count record by source
                var listJobJson = _collectionJob.Aggregate()
                    .Match(
                        new BsonDocument("created_date_crawl_job",
                            new BsonDocument
                            {
                                { "$gte", from },
                                { "$lte", to }
                            }))
                        .Group(new BsonDocument {
                                    { "_id",
                                        new BsonDocument
                                        {
                                            { "source", "$source" },
                                            { "created_date_crawl_job_string", "$created_date_crawl_job_string" }
                                        }},
                                    { "count", new BsonDocument("$sum", 1) }
                            })
                        .ToList().ToJson();

                var listJob = Newtonsoft.Json.JsonConvert.DeserializeObject<List<WapperJob>>(listJobJson);

                // fulljoin listJob vs listError
                var mergelistJob = listError.FullGroupJoin(
                   listJob,
                   a => a.created_date_string,
                   b => b._id.created_date_crawl_job_string,
                   (a, b, t) => new MergeJob()
                   {
                       CreateDateString = a,
                       jobErrors = b.ToList(),
                       Jobs = t.ToList()
                   }).ToList();


                // build model to response
                if (mergelistJob != null && mergelistJob.Any())
                {
                    foreach (var merge in mergelistJob)
                    {

                        if (merge.Jobs != null && merge.Jobs.Any())
                        {
                            foreach (var itemJob in merge.Jobs)
                            {
                                var result = new GetJobByDateResult();
                                if (merge.jobErrors != null && merge.jobErrors.Any(x => x.source == itemJob._id.source))
                                {
                                    result.HasError = true;
                                    result.JobErrors = merge.jobErrors.Where(x => x.source == itemJob._id.source)
                                                                      .OrderByDescending(x => x.created_date).ToList();
                                }
                                else
                                {
                                    result.HasError = false;
                                    result.JobErrors = new List<Job_Error>();
                                }

                                result.Website = itemJob._id.source;
                                result.CreatedDate = merge.CreateDateString;
                                result.CreatedDate_DateTime = HelperExtension.ConvertStringToDate(merge.CreateDateString);
                                result.TotalRecordCrawl = itemJob.count;
                                listJobByDateResult.Add(result);
                            }
                        }
                        else
                        {
                            if (merge.jobErrors != null && merge.jobErrors.Any())
                            {
                                foreach (var source in Constant.SOURCES)
                                {
                                    var errorDetail = merge.jobErrors.Where(x => x.source == source)
                                                                     .OrderByDescending(x => x.created_date).ToList();
                                    var result = new GetJobByDateResult();
                                    result.HasError = errorDetail.Any();
                                    result.JobErrors = errorDetail;
                                    result.CreatedDate = merge.CreateDateString;
                                    result.CreatedDate_DateTime = HelperExtension.ConvertStringToDate(merge.CreateDateString);
                                    result.Website = source;
                                    result.TotalRecordCrawl = 0;
                                    listJobByDateResult.Add(result);
                                }
                            }
                        }
                    }


                    // map list result to list reponse
                    if (listJobByDateResult.Any())
                    {
                        var listDateJobResponse = new List<DataListJob>();
                        
                        var createdDatesDistinct = listJobByDateResult.Select(x => x.CreatedDate).Distinct();
                        foreach (var createdDate in createdDatesDistinct)
                        {
                            var jobByDates = listJobByDateResult.Where(x => x.CreatedDate == createdDate);
                            var jobByDateItem = new DataListJob();
                            var jobCrawlStatisticals = new List<JobCrawlStatistical>();
                            foreach (var jobByDate in jobByDates)
                            {
                                var jobCrawlItem = new JobCrawlStatistical();
                                jobCrawlItem.SoBanGhi = jobByDate.TotalRecordCrawl;
                                jobCrawlItem.Nguon = jobByDate.Website;
                                jobCrawlItem.TrangThai = jobByDate.HasError;
                                jobCrawlItem.ChiTietLoi = jobByDate.JobErrors;
                                jobCrawlStatisticals.Add(jobCrawlItem);
                            }

                            jobByDateItem.Ngay = createdDate;
                            jobByDateItem.CreatedDateOrder = HelperExtension.ConvertStringToDate(createdDate);
                            jobByDateItem.TongSoBanGhi = jobByDates.Sum(x => x.TotalRecordCrawl);
                            jobByDateItem.DanhSachBanGhi = jobCrawlStatisticals;
                            listDateJobResponse.Add(jobByDateItem);
                        }

                        var totalCount = createdDatesDistinct.Count();
                        var listDateJobResponsePagning = listDateJobResponse.OrderByDescending(x => x.CreatedDateOrder)
                                                                        .Skip((pageIndex - 1) * pageSize)
                                                                        .Take(pageSize);

                        return new PaginatedList<DataListJob>
                        {
                            DataList = listDateJobResponsePagning,
                            TotalRow = totalCount,
                            PageIndex = pageIndex,
                            PageSize = pageSize
                        };

                    }
                    else
                    {
                        _logger.LogInformation("listJobByDateResult not found");  
                    }
                }
                else
                {
                    _logger.LogInformation("List Job not found");
                }
                return new PaginatedList<DataListJob>() { PageIndex = pageIndex, PageSize = pageSize };
                //return jobByDateResponse;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex.Message);
                return new PaginatedList<DataListJob>() { PageIndex = pageIndex, PageSize = pageSize };
            }
        }

    }
}
