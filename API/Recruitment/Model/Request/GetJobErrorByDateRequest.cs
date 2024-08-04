using System.ComponentModel.DataAnnotations;

namespace Recruitment.Model.CrawlModel
{
    public class GetJobErrorByDateRequest
    {
        public string? IdError { get; set; }
        public string? Source { get; set; }
        public string From { get; set; }
        public string To { get; set; }
    }
}
