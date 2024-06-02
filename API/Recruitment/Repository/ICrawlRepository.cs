using Recruitment.Model;
using Recruitment.Model.Response;
using Recruitment.Repository.Entities;

namespace Recruitment.Repository
{
    public interface ICrawlRepository
    {
        Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string website, DateTime from, DateTime to);

        Task<List<GetJobByDateResponse>> GetJobByDateAsync(DateTime from, DateTime to);
    }
}
