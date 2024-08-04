using Recruitment.Common;
using Recruitment.Model;
using Recruitment.Model.Response;
using Recruitment.Repository.Entities;

namespace Recruitment.Repository
{
    public interface ICrawlRepository
    {
        Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string idError, string source, DateTime from, DateTime to);

        Task<PaginatedList<DataListJob>> GetJobByDateAsync(DateTime from, DateTime to, int pageIndex, int pageSize);
    }
}
