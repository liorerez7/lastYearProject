////const DEMO_RESULTS = [
////  // basicselect
////  { schema: 'finalEmp', test_name: 'basicselect_10u', query_type: 'basicselect', load_level: 10,
////    mysql_avg_duration: 0.293, mysql_p95: 0.47, mysql_stddev: 0.06, mysql_count: 54,
////    postgres_avg_duration: 0.445, postgres_p95: 0.47, postgres_stddev: 0.01, postgres_count: 12,
////    winner: 'MySQL', difference_percent: 51.8
////  },
////  { schema: 'finalEmp', test_name: 'basicselect_40u', query_type: 'basicselect', load_level: 40,
////    mysql_avg_duration: 0.296, mysql_p95: 0.32, mysql_stddev: 0.04, mysql_count: 80,
////    postgres_avg_duration: 0.451, postgres_p95: 0.46, postgres_stddev: 0.01, postgres_count: 9,
////    winner: 'MySQL', difference_percent: 52.6
////  },
////
////  // deepjoin
////  { schema: 'finalEmp', test_name: 'deepjoin_10u', query_type: 'deepjoin', load_level: 10,
////    mysql_avg_duration: 0.456, mysql_p95: 0.48, mysql_stddev: 0.04, mysql_count: 60,
////    postgres_avg_duration: 0.600, postgres_p95: 0.62, postgres_stddev: 0.01, postgres_count: 16,
////    winner: 'MySQL', difference_percent: 31.5
////  },
////  { schema: 'finalEmp', test_name: 'deepjoin_40u', query_type: 'deepjoin', load_level: 40,
////    mysql_avg_duration: 0.450, mysql_p95: 0.48, mysql_stddev: 0.04, mysql_count: 135,
////    postgres_avg_duration: 0.603, postgres_p95: 0.62, postgres_stddev: 0.02, postgres_count: 15,
////    winner: 'MySQL', difference_percent: 34.0
////  },
////
////  // pagination
////  { schema: 'finalEmp', test_name: 'pagination_10u', query_type: 'pagination', load_level: 10,
////    mysql_avg_duration: 0.153, mysql_p95: 0.16, mysql_stddev: 0.02, mysql_count: 162,
////    postgres_avg_duration: 0.151, postgres_p95: 0.16, postgres_stddev: 0.00, postgres_count: 27,
////    winner: 'PostgreSQL', difference_percent: 1.2
////  },
////  { schema: 'finalEmp', test_name: 'pagination_40u', query_type: 'pagination', load_level: 40,
////    mysql_avg_duration: 0.151, mysql_p95: 0.16, mysql_stddev: 0.00, mysql_count: 215,
////    postgres_avg_duration: 0.150, postgres_p95: 0.16, postgres_stddev: 0.00, postgres_count: 26,
////    winner: 'PostgreSQL', difference_percent: 0.3
////  },
////
////  // filtered
////  { schema: 'finalEmp', test_name: 'filtered_10u', query_type: 'filtered', load_level: 10,
////    mysql_avg_duration: 0.304, mysql_p95: 0.32, mysql_stddev: 0.03, mysql_count: 82,
////    postgres_avg_duration: 0.450, postgres_p95: 0.47, postgres_stddev: 0.01, postgres_count: 16,
////    winner: 'MySQL', difference_percent: 48.1
////  },
////  { schema: 'finalEmp', test_name: 'filtered_40u', query_type: 'filtered', load_level: 40,
////    mysql_avg_duration: 0.295, mysql_p95: 0.32, mysql_stddev: 0.04, mysql_count: 123,
////    postgres_avg_duration: 0.455, postgres_p95: 0.46, postgres_stddev: 0.01, postgres_count: 15,
////    winner: 'MySQL', difference_percent: 54.2
////  },
////
////  // aggregation
////  { schema: 'finalEmp', test_name: 'aggregation_10u', query_type: 'aggregation', load_level: 10,
////    mysql_avg_duration: 0.158, mysql_p95: 0.17, mysql_stddev: 0.02, mysql_count: 203,
////    postgres_avg_duration: 0.299, postgres_p95: 0.31, postgres_stddev: 0.01, postgres_count: 41,
////    winner: 'MySQL', difference_percent: 88.8
////  },
////  { schema: 'finalEmp', test_name: 'aggregation_40u', query_type: 'aggregation', load_level: 40,
////    mysql_avg_duration: 0.156, mysql_p95: 0.16, mysql_stddev: 0.00, mysql_count: 280,
////    postgres_avg_duration: 0.302, postgres_p95: 0.32, postgres_stddev: 0.00, postgres_count: 40,
////    winner: 'MySQL', difference_percent: 94.2
////  },
////
////  // groupby
////  { schema: 'finalEmp', test_name: 'groupby_10u', query_type: 'groupby', load_level: 10,
////    mysql_avg_duration: 0.158, mysql_p95: 0.16, mysql_stddev: 0.02, mysql_count: 103,
////    postgres_avg_duration: 0.304, postgres_p95: 0.33, postgres_stddev: 0.01, postgres_count: 13,
////    winner: 'MySQL', difference_percent: 92.8
////  },
////  { schema: 'finalEmp', test_name: 'groupby_40u', query_type: 'groupby', load_level: 40,
////    mysql_avg_duration: 0.157, mysql_p95: 0.17, mysql_stddev: 0.00, mysql_count: 156,
////    postgres_avg_duration: 0.301, postgres_p95: 0.33, postgres_stddev: 0.01, postgres_count: 21,
////    winner: 'MySQL', difference_percent: 92.4
////  },
////
////  // purecount
////  { schema: 'finalEmp', test_name: 'purecount_10u', query_type: 'purecount', load_level: 10,
////    mysql_avg_duration: 0.418, mysql_p95: 0.79, mysql_stddev: 0.23, mysql_count: 147,
////    postgres_avg_duration: 0.205, postgres_p95: 0.35, postgres_stddev: 0.04, postgres_count: 28,
////    winner: 'PostgreSQL', difference_percent: 103.9
////  },
////  { schema: 'finalEmp', test_name: 'purecount_40u', query_type: 'purecount', load_level: 40,
////    mysql_avg_duration: 0.372, mysql_p95: 0.53, mysql_stddev: 0.08, mysql_count: 206,
////    postgres_avg_duration: 0.210, postgres_p95: 0.27, postgres_stddev: 0.02, postgres_count: 26,
////    winner: 'PostgreSQL', difference_percent: 76.8
////  },
////];
////
////export default DEMO_RESULTS;
//
//// components/demoResults.js
//// Story: 6 tables total, 2 tiny, biggest ~1GB, others 200–400MB.
//// Target users/data: up to ~3GB on t3.micro → moderate latencies, visible sensitivity to 40u load.
//// Locust users: 10u / 40u. Winner logic: lower avg duration is faster.
//// difference_percent computed as: ((slower - faster) / faster) * 100
//
//const DEMO_RESULTS = [
//  // ─────────────────────────── BASIC SELECT (OLTP-light) ───────────────────────────
//  // MySQL קלילה ומהירה מעט יותר בבסיס; 40u מעלה זמני תגובה ~+18–20%
//  { schema: 'mydb', test_name: 'basicselect_10u', query_type: 'basicselect', load_level: 10,
//    mysql_avg_duration: 0.220, mysql_p95: 0.280, mysql_stddev: 0.040, mysql_count: 180,
//    postgres_avg_duration: 0.260, postgres_p95: 0.340, postgres_stddev: 0.050, postgres_count: 182,
//    winner: 'MySQL', difference_percent: 18.2
//  },
//  { schema: 'mydb', test_name: 'basicselect_40u', query_type: 'basicselect', load_level: 40,
//    mysql_avg_duration: 0.260, mysql_p95: 0.330, mysql_stddev: 0.055, mysql_count: 260,
//    postgres_avg_duration: 0.310, postgres_p95: 0.400, postgres_stddev: 0.060, postgres_count: 262,
//    winner: 'MySQL', difference_percent: 19.2
//  },
//
//  // ─────────────────────────────── FILTERED (WHERE/INDEX) ───────────────────────────────
//  // MySQL מובילה במסננים (דפוס OLTP) בפער מתון-בינוני; 40u מגדיל מעט את הפער
//  { schema: 'mydb', test_name: 'filtered_10u', query_type: 'filtered', load_level: 10,
//    mysql_avg_duration: 0.300, mysql_p95: 0.360, mysql_stddev: 0.040, mysql_count: 120,
//    postgres_avg_duration: 0.390, postgres_p95: 0.470, postgres_stddev: 0.050, postgres_count: 122,
//    winner: 'MySQL', difference_percent: 30.0
//  },
//  { schema: 'mydb', test_name: 'filtered_40u', query_type: 'filtered', load_level: 40,
//    mysql_avg_duration: 0.350, mysql_p95: 0.420, mysql_stddev: 0.050, mysql_count: 200,
//    postgres_avg_duration: 0.460, postgres_p95: 0.560, postgres_stddev: 0.060, postgres_count: 201,
//    winner: 'MySQL', difference_percent: 31.4
//  },
//
//  // ──────────────────────────────── AGGREGATION (SUM/AVG) ────────────────────────────────
//  // MySQL זריזה קלות באגרגציות פשוטות; 40u מעלה זמני תגובה
//  { schema: 'mydb', test_name: 'aggregation_10u', query_type: 'aggregation', load_level: 10,
//    mysql_avg_duration: 0.200, mysql_p95: 0.240, mysql_stddev: 0.025, mysql_count: 220,
//    postgres_avg_duration: 0.240, postgres_p95: 0.300, postgres_stddev: 0.030, postgres_count: 221,
//    winner: 'MySQL', difference_percent: 20.0
//  },
//  { schema: 'mydb', test_name: 'aggregation_40u', query_type: 'aggregation', load_level: 40,
//    mysql_avg_duration: 0.240, mysql_p95: 0.300, mysql_stddev: 0.030, mysql_count: 300,
//    postgres_avg_duration: 0.290, postgres_p95: 0.360, postgres_stddev: 0.040, postgres_count: 302,
//    winner: 'MySQL', difference_percent: 20.8
//  },
//
//  // ───────────────────────────── GROUP BY (OLAP-ish קטנות/בינוניות) ─────────────────────────────
//  // MySQL מובילה במקצת; 40u מחמיר מעט את הפער
//  { schema: 'mydb', test_name: 'groupby_10u', query_type: 'groupby', load_level: 10,
//    mysql_avg_duration: 0.210, mysql_p95: 0.260, mysql_stddev: 0.030, mysql_count: 140,
//    postgres_avg_duration: 0.250, postgres_p95: 0.320, postgres_stddev: 0.040, postgres_count: 141,
//    winner: 'MySQL', difference_percent: 19.0
//  },
//  { schema: 'mydb', test_name: 'groupby_40u', query_type: 'groupby', load_level: 40,
//    mysql_avg_duration: 0.250, mysql_p95: 0.320, mysql_stddev: 0.035, mysql_count: 220,
//    postgres_avg_duration: 0.310, postgres_p95: 0.390, postgres_stddev: 0.045, postgres_count: 221,
//    winner: 'MySQL', difference_percent: 24.0
//  },
//
//  // ──────────────────────────────── PAGINATION (ממוצע אתר “רגיל”) ────────────────────────────────
//  // PostgreSQL מעט מהירה יותר (cursor/planner); ההפרש קטן ועקבי
//  { schema: 'mydb', test_name: 'pagination_10u', query_type: 'pagination', load_level: 10,
//    mysql_avg_duration: 0.160, mysql_p95: 0.190, mysql_stddev: 0.015, mysql_count: 200,
//    postgres_avg_duration: 0.150, postgres_p95: 0.180, postgres_stddev: 0.015, postgres_count: 202,
//    winner: 'PostgreSQL', difference_percent: 6.7
//  },
//  { schema: 'mydb', test_name: 'pagination_40u', query_type: 'pagination', load_level: 40,
//    mysql_avg_duration: 0.190, mysql_p95: 0.220, mysql_stddev: 0.018, mysql_count: 280,
//    postgres_avg_duration: 0.180, postgres_p95: 0.210, postgres_stddev: 0.018, postgres_count: 282,
//    winner: 'PostgreSQL', difference_percent: 5.6
//  },
//
//  // ─────────────────────────────────── DEEP JOIN (t6/t7 גדולות) ───────────────────────────────────
//  // PostgreSQL מובילה קלות, במיוחד ב-40u (planner, join strategy)
//  { schema: 'mydb', test_name: 'deepjoin_10u', query_type: 'deepjoin', load_level: 10,
//    mysql_avg_duration: 0.580, mysql_p95: 0.680, mysql_stddev: 0.060, mysql_count: 80,
//    postgres_avg_duration: 0.540, postgres_p95: 0.630, postgres_stddev: 0.050, postgres_count: 82,
//    winner: 'PostgreSQL', difference_percent: 7.4
//  },
//  { schema: 'mydb', test_name: 'deepjoin_40u', query_type: 'deepjoin', load_level: 40,
//    mysql_avg_duration: 0.700, mysql_p95: 0.820, mysql_stddev: 0.080, mysql_count: 160,
//    postgres_avg_duration: 0.620, postgres_p95: 0.740, postgres_stddev: 0.070, postgres_count: 162,
//    winner: 'PostgreSQL', difference_percent: 12.9
//  },
//
//  // ───────────────────────────────────── PURE COUNT (COUNT(*)) ─────────────────────────────────────
//  // PostgreSQL עדיפה משמעותית (סיפור ידוע); 40u מגדיל את ההבדל באפליקטיביות
//  { schema: 'mydb', test_name: 'purecount_10u', query_type: 'purecount', load_level: 10,
//    mysql_avg_duration: 0.420, mysql_p95: 0.700, mysql_stddev: 0.100, mysql_count: 100,
//    postgres_avg_duration: 0.250, postgres_p95: 0.400, postgres_stddev: 0.060, postgres_count: 101,
//    winner: 'PostgreSQL', difference_percent: 68.0
//  },
//  { schema: 'mydb', test_name: 'purecount_40u', query_type: 'purecount', load_level: 40,
//    mysql_avg_duration: 0.520, mysql_p95: 0.850, mysql_stddev: 0.120, mysql_count: 160,
//    postgres_avg_duration: 0.290, postgres_p95: 0.460, postgres_stddev: 0.070, postgres_count: 161,
//    winner: 'PostgreSQL', difference_percent: 79.3
//  },
//];
//
//export default DEMO_RESULTS;


// components/demoResults.js
// Story setup:
// - 6 tables total (2 tiny, 1 ~1GB, others 200–400MB)
// - Target audience up to ~3GB on t3.micro (modest CPU/mem), Locust @ 10u / 40u
// - Winners chosen by lower avg duration (seconds)
// - difference_percent = ((slower - faster) / faster) * 100  [“X% faster”]

const DEMO_RESULTS = [
  // ───────── BASIC SELECT (OLTP-light) ─────────
  // MySQL מעט מהירה יותר; 40u מעלה זמני תגובה ~+18–20%
  { schema: 'mydb', test_name: 'basicselect_10u', query_type: 'basicselect', load_level: 10,
    mysql_avg_duration: 0.220, mysql_p95: 0.285, mysql_stddev: 0.041, mysql_count: 176,
    postgres_avg_duration: 0.260, postgres_p95: 0.345, postgres_stddev: 0.052, postgres_count: 169,
    winner: 'MySQL', difference_percent: 18.2
  },
  { schema: 'mydb', test_name: 'basicselect_40u', query_type: 'basicselect', load_level: 40,
    mysql_avg_duration: 0.260, mysql_p95: 0.335, mysql_stddev: 0.055, mysql_count: 422,
    postgres_avg_duration: 0.310, postgres_p95: 0.405, postgres_stddev: 0.061, postgres_count: 408,
    winner: 'MySQL', difference_percent: 19.2
  },

  // ───────── FILTERED (WHERE/INDEX) ─────────
  // MySQL מובילה במסננים; 40u מגדיל מעט את הפער
  { schema: 'mydb', test_name: 'filtered_10u', query_type: 'filtered', load_level: 10,
    mysql_avg_duration: 0.300, mysql_p95: 0.362, mysql_stddev: 0.041, mysql_count: 131,
    postgres_avg_duration: 0.390, postgres_p95: 0.472, postgres_stddev: 0.053, postgres_count: 124,
    winner: 'MySQL', difference_percent: 30.0
  },
  { schema: 'mydb', test_name: 'filtered_40u', query_type: 'filtered', load_level: 40,
    mysql_avg_duration: 0.350, mysql_p95: 0.426, mysql_stddev: 0.052, mysql_count: 299,
    postgres_avg_duration: 0.460, postgres_p95: 0.565, postgres_stddev: 0.061, postgres_count: 287,
    winner: 'MySQL', difference_percent: 31.4
  },

  // ───────── AGGREGATION (SUM/AVG) ─────────
  // MySQL זריזה קלות באגרגציות פשוטות; רגישות לעומס
  { schema: 'mydb', test_name: 'aggregation_10u', query_type: 'aggregation', load_level: 10,
    mysql_avg_duration: 0.200, mysql_p95: 0.246, mysql_stddev: 0.026, mysql_count: 237,
    postgres_avg_duration: 0.240, postgres_p95: 0.300, postgres_stddev: 0.031, postgres_count: 229,
    winner: 'MySQL', difference_percent: 20.0
  },
  { schema: 'mydb', test_name: 'aggregation_40u', query_type: 'aggregation', load_level: 40,
    mysql_avg_duration: 0.240, mysql_p95: 0.301, mysql_stddev: 0.033, mysql_count: 318,
    postgres_avg_duration: 0.290, postgres_p95: 0.361, postgres_stddev: 0.039, postgres_count: 305,
    winner: 'MySQL', difference_percent: 20.8
  },

  // ───────── GROUP BY (OLAP-ish קטנות/בינוניות) ─────────
  // MySQL מובילה במקצת; ב-40u יש רעש/variance גבוה יותר
  { schema: 'mydb', test_name: 'groupby_10u', query_type: 'groupby', load_level: 10,
    mysql_avg_duration: 0.210, mysql_p95: 0.262, mysql_stddev: 0.031, mysql_count: 152,
    postgres_avg_duration: 0.250, postgres_p95: 0.320, postgres_stddev: 0.041, postgres_count: 147,
    winner: 'MySQL', difference_percent: 19.1
  },
  { schema: 'mydb', test_name: 'groupby_40u', query_type: 'groupby', load_level: 40,
    mysql_avg_duration: 0.265, mysql_p95: 0.340, mysql_stddev: 0.038, mysql_count: 226,
    postgres_avg_duration: 0.330, postgres_p95: 0.410, postgres_stddev: 0.048, postgres_count: 214,
    winner: 'MySQL', difference_percent: 24.5
  },

  // ───────── PAGINATION (אתר “רגיל”) ─────────
  // PostgreSQL מעט מהירה יותר (planner/cursors); הפרש קטן אבל עקבי
  { schema: 'mydb', test_name: 'pagination_10u', query_type: 'pagination', load_level: 10,
    mysql_avg_duration: 0.165, mysql_p95: 0.195, mysql_stddev: 0.017, mysql_count: 212,
    postgres_avg_duration: 0.155, postgres_p95: 0.185, postgres_stddev: 0.016, postgres_count: 224,
    winner: 'PostgreSQL', difference_percent: 6.5
  },
  { schema: 'mydb', test_name: 'pagination_40u', query_type: 'pagination', load_level: 40,
    mysql_avg_duration: 0.195, mysql_p95: 0.225, mysql_stddev: 0.019, mysql_count: 284,
    postgres_avg_duration: 0.185, postgres_p95: 0.215, postgres_stddev: 0.018, postgres_count: 297,
    winner: 'PostgreSQL', difference_percent: 5.4
  },

  // ───────── DEEP JOIN (t6/t7 גדולות) ─────────
  // כאן "טוויסט": MySQL מנצח קלות (קומפוזיט אינדקס + planner heuristics)
  { schema: 'mydb', test_name: 'deepjoin_10u', query_type: 'deepjoin', load_level: 10,
    mysql_avg_duration: 0.560, mysql_p95: 0.670, mysql_stddev: 0.066, mysql_count: 78,
    postgres_avg_duration: 0.575, postgres_p95: 0.690, postgres_stddev: 0.071, postgres_count: 74,
    winner: 'MySQL', difference_percent: 2.7
  },
  { schema: 'mydb', test_name: 'deepjoin_40u', query_type: 'deepjoin', load_level: 40,
    mysql_avg_duration: 0.710, mysql_p95: 0.835, mysql_stddev: 0.082, mysql_count: 161,
    postgres_avg_duration: 0.740, postgres_p95: 0.870, postgres_stddev: 0.089, postgres_count: 154,
    winner: 'MySQL', difference_percent: 4.2
  },

  // ───────── PURE COUNT (COUNT(*)) ─────────
  // PostgreSQL עדיפה משמעותית; ב-40u הפער אף גדל מעט
  { schema: 'mydb', test_name: 'purecount_10u', query_type: 'purecount', load_level: 10,
    mysql_avg_duration: 1.430, mysql_p95: 1.732, mysql_stddev: 0.233, mysql_count: 23,
    postgres_avg_duration: 0.260, postgres_p95: 0.405, postgres_stddev: 0.062, postgres_count: 101,
    winner: 'PostgreSQL', difference_percent: 65.4
  },
  { schema: 'mydb', test_name: 'purecount_40u', query_type: 'purecount', load_level: 40,
    mysql_avg_duration: 2.520, mysql_p95: 0.860, mysql_stddev: 0.121, mysql_count: 43,
    postgres_avg_duration: 0.410, postgres_p95: 0.470, postgres_stddev: 0.071, postgres_count: 164,
    winner: 'PostgreSQL', difference_percent: 67.7
  },
];

export default DEMO_RESULTS;
