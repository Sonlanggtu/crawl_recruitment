using Recruitment.Repository.Entities;
using System.Text.Json.Serialization;

namespace Recruitment.Model.Response
{
    public class GetJobByDateResponse
    {

        //public int TotalRow { get; set; }

        public List<DataListJob> DataList { get; set; } = new List<DataListJob>();



    }


    public class DataListJob
    {
        public string Ngay { get; set; }
        public int TongSoBanGhi { get; set; }
        public List<JobCrawlStatistical> DanhSachBanGhi { get; set; } = new List<JobCrawlStatistical>();

        [JsonIgnore]
        public DateTime CreatedDateOrder { get; set; }

    }

    public class JobCrawlStatistical
    {
        public string Nguon { get; set; }
        public bool TrangThai { get; set; }
        public int SoBanGhi { get; set; }
        public List<Job_Error> ChiTietLoi { get; set; } = new List<Job_Error>();
    }

}
