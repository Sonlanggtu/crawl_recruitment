using System.ComponentModel.DataAnnotations;

namespace Recruitment.Model.CrawlModel
{
    public class GetJobByDateRequest
    {
        public string From { get; set; } = string.Empty;
        public string To { get; set; } = string.Empty;
        public int PageIndex { get; set; } = 1;
        public int PageSize { get; set; } = 10;

    }
}
