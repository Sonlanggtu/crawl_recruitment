using System.ComponentModel.DataAnnotations;

namespace Recruitment.Model.CrawlModel
{
    public class GetJobByDateRequest
    {
        public string From { get; set; }
        public string To { get; set; }
    }
}
