using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
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
        public async Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string website, string from, string to)
        {
            try
            {
                _logger.LogInformation($"Start GetJobErrorByDateAsync website: {website} - from: {from} - to: {to}");

                DateTime fromParsed = DateTime.ParseExact(from, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);
                DateTime toParsed = DateTime.ParseExact(to, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);

                var res = await _crawlRepository.GetJobErrorByDateAsync(website, fromParsed, toParsed);
                return res;
            }
            catch (Exception ex)
            {
                _logger.LogError($"GetJobErrorByDateAsync - {ex.Message}");
                return new List<JobErrorResponse>();
            }
           
        }

        public async Task<List<GetJobByDateResponse>> GetJobByDateAsync(string from, string to)
        {
            try
            {
                DateTime fromParsed = DateTime.ParseExact(from, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);
                DateTime toParsed = DateTime.ParseExact(to, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None);

                var res = await _crawlRepository.GetJobByDateAsync(fromParsed, toParsed);
                return res;
            }
            catch (Exception ex)
            {
                _logger.LogError($"GetJobByDateAsync - {ex.Message}");
                return new List<GetJobByDateResponse>();
            }
            
        }

    }
}
