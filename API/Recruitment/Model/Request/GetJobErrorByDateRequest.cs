using System.ComponentModel.DataAnnotations;

namespace Recruitment.Model.CrawlModel
{
    public class GetJobErrorByDateRequest
    {
        public string? Website { get; set; }
       
        public string From { get; set; }

        public string To { get; set; }
    }
}
