using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Recruitment.Common
{
    public class PaginatedList<T> where T : class
    {
        public IEnumerable<T> DataList { get; set; }
        public int TotalRow { get; set; }
        public int PageIndex { get; set; }
        public int PageSize { get; set; }
        public int TotalPages => (int)Math.Ceiling((double)TotalRow / PageSize);
    }
}
