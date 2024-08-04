using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Recruitment.Common;
using Recruitment.Model;
using Recruitment.Model.Response;
using Recruitment.Repository;
using Recruitment.Repository.Entities;
using System.Globalization;

namespace Recruitment.Services
{
    public class CrawlService : ICrawlService
    {
        private readonly ILogger<CrawlService> _logger;
        private readonly ICrawlRepository _crawlRepository;

        public CrawlService(ILogger<CrawlService> logger, ICrawlRepository crawlRepository)
        {
            _logger = logger;
            _crawlRepository = crawlRepository;

        }
        public async Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string idError, string source, string from, string to)
        {
            try
            {
                _logger.LogInformation($"Start GetJobErrorByDateAsync idError:{idError} - source: {source} - from: {from} - to: {to}");

                DateTime fromParsed = DateTime.ParseExact(from, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);
                DateTime toParsed = DateTime.ParseExact(to, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);

                var res = await _crawlRepository.GetJobErrorByDateAsync(idError, source, fromParsed, toParsed);
                return res;
            }
            catch (Exception ex)
            {
                _logger.LogError($"GetJobErrorByDateAsync - {ex.Message}");
                return new List<JobErrorResponse>();
            }
           
        }

        public async Task<PaginatedList<DataListJob>> GetJobByDateAsync(string from, string to, int pageIndex, int pageSize)
        {
            try
            {
                DateTime fromParsed = DateTime.ParseExact(from, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);
                DateTime toParsed = DateTime.ParseExact(to, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);

                var res = await _crawlRepository.GetJobByDateAsync(fromParsed, toParsed, pageIndex, pageSize);
                return res;
            }
            catch (Exception ex)
            {
                _logger.LogError($"GetJobByDateAsync - {ex.Message}");
                return new PaginatedList<DataListJob>() { PageIndex =  pageIndex, PageSize = pageSize};
            }
            
        }

    }
}
