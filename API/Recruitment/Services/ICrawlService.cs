using Recruitment.Common;
using Recruitment.Model;
using Recruitment.Model.Response;
using Recruitment.Repository.Entities;
using System.Runtime.CompilerServices;

namespace Recruitment.Services
{
    public interface ICrawlService
    {
        Task<PaginatedList<DataListJob>> GetJobByDateAsync(string from, string to, int pageIndex, int pageSize);
        Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string idError, string source, string from, string to);
    }
}
