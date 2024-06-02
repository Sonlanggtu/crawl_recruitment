using MongoDB.Bson.Serialization.Attributes;

namespace Recruitment.Model.Response
{
    public class JobErrorResponse
    {
        public string IdRrror { get; set; }
        public string Source { get; set; }
        public string ErrorMessage { get; set; }
        public string TimeCrawl { get; set; }
        public string CreatedDate { get; set; }
    }
}
