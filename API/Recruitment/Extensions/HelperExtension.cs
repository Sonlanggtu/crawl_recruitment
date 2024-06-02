using Amazon.Runtime.Internal.Transform;
using Microsoft.AspNetCore.Http;
using System.Globalization;

namespace Recruitment.Extensions
{
    public static class HelperExtension
    {
        public static IList<TR> FullOuterGroupJoin<TA, TB, TK, TR>(
            this IEnumerable<TA> a,
            IEnumerable<TB> b,
            Func<TA, TK> selectKeyA,
            Func<TB, TK> selectKeyB,
            Func<IEnumerable<TA>, IEnumerable<TB>, TK, TR> projection,
            IEqualityComparer<TK> cmp = null)
        {
            cmp = cmp ?? EqualityComparer<TK>.Default;
            var alookup = a.ToLookup(selectKeyA, cmp);
            var blookup = b.ToLookup(selectKeyB, cmp);

            var keys = new HashSet<TK>(alookup.Select(p => p.Key), cmp);
            keys.UnionWith(blookup.Select(p => p.Key));

            var join = from key in keys
                       let xa = alookup[key]
                       let xb = blookup[key]
                       select projection(xa, xb, key);

            return join.ToList();
        }

        internal static IList<TR> FullOuterJoin<TA, TB, TK, TR>(
            this IEnumerable<TA> a,
            IEnumerable<TB> b,
            Func<TA, TK> selectKeyA,
            Func<TB, TK> selectKeyB,
            Func<TA, TB, TK, TR> projection,
            TA defaultA = default(TA),
            TB defaultB = default(TB),
            IEqualityComparer<TK> cmp = null)
        {
            cmp = cmp ?? EqualityComparer<TK>.Default;
            var alookup = a.ToLookup(selectKeyA, cmp);
            var blookup = b.ToLookup(selectKeyB, cmp);

            var keys = new HashSet<TK>(alookup.Select(p => p.Key), cmp);
            keys.UnionWith(blookup.Select(p => p.Key));

            var join = from key in keys
                       from xa in alookup[key].DefaultIfEmpty(defaultA)
                       from xb in blookup[key].DefaultIfEmpty(defaultB)
                       select projection(xa, xb, key);

            return join.ToList();
        }


        public static DateTime ConvertStringToDate(string date)
        {
            DateTime parsed;

            bool valid = DateTime.TryParseExact(date, "dd/MM/yyyy",
                                                CultureInfo.InvariantCulture,
                                                DateTimeStyles.None,
                                                out parsed);
            return parsed;
        }
    }
}
