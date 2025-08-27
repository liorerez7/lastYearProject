const DEMO_RESULTS = [
  // basicselect
  { schema: 'finalEmp', test_name: 'basicselect_10u', query_type: 'basicselect', load_level: 10,
    mysql_avg_duration: 0.293, mysql_p95: 0.47, mysql_stddev: 0.06, mysql_count: 54,
    postgres_avg_duration: 0.445, postgres_p95: 0.47, postgres_stddev: 0.01, postgres_count: 12,
    winner: 'MySQL', difference_percent: 51.8
  },
  { schema: 'finalEmp', test_name: 'basicselect_40u', query_type: 'basicselect', load_level: 40,
    mysql_avg_duration: 0.296, mysql_p95: 0.32, mysql_stddev: 0.04, mysql_count: 80,
    postgres_avg_duration: 0.451, postgres_p95: 0.46, postgres_stddev: 0.01, postgres_count: 9,
    winner: 'MySQL', difference_percent: 52.6
  },

  // deepjoin
  { schema: 'finalEmp', test_name: 'deepjoin_10u', query_type: 'deepjoin', load_level: 10,
    mysql_avg_duration: 0.456, mysql_p95: 0.48, mysql_stddev: 0.04, mysql_count: 60,
    postgres_avg_duration: 0.600, postgres_p95: 0.62, postgres_stddev: 0.01, postgres_count: 16,
    winner: 'MySQL', difference_percent: 31.5
  },
  { schema: 'finalEmp', test_name: 'deepjoin_40u', query_type: 'deepjoin', load_level: 40,
    mysql_avg_duration: 0.450, mysql_p95: 0.48, mysql_stddev: 0.04, mysql_count: 135,
    postgres_avg_duration: 0.603, postgres_p95: 0.62, postgres_stddev: 0.02, postgres_count: 15,
    winner: 'MySQL', difference_percent: 34.0
  },

  // pagination
  { schema: 'finalEmp', test_name: 'pagination_10u', query_type: 'pagination', load_level: 10,
    mysql_avg_duration: 0.153, mysql_p95: 0.16, mysql_stddev: 0.02, mysql_count: 162,
    postgres_avg_duration: 0.151, postgres_p95: 0.16, postgres_stddev: 0.00, postgres_count: 27,
    winner: 'PostgreSQL', difference_percent: 1.2
  },
  { schema: 'finalEmp', test_name: 'pagination_40u', query_type: 'pagination', load_level: 40,
    mysql_avg_duration: 0.151, mysql_p95: 0.16, mysql_stddev: 0.00, mysql_count: 215,
    postgres_avg_duration: 0.150, postgres_p95: 0.16, postgres_stddev: 0.00, postgres_count: 26,
    winner: 'PostgreSQL', difference_percent: 0.3
  },

  // filtered
  { schema: 'finalEmp', test_name: 'filtered_10u', query_type: 'filtered', load_level: 10,
    mysql_avg_duration: 0.304, mysql_p95: 0.32, mysql_stddev: 0.03, mysql_count: 82,
    postgres_avg_duration: 0.450, postgres_p95: 0.47, postgres_stddev: 0.01, postgres_count: 16,
    winner: 'MySQL', difference_percent: 48.1
  },
  { schema: 'finalEmp', test_name: 'filtered_40u', query_type: 'filtered', load_level: 40,
    mysql_avg_duration: 0.295, mysql_p95: 0.32, mysql_stddev: 0.04, mysql_count: 123,
    postgres_avg_duration: 0.455, postgres_p95: 0.46, postgres_stddev: 0.01, postgres_count: 15,
    winner: 'MySQL', difference_percent: 54.2
  },

  // aggregation
  { schema: 'finalEmp', test_name: 'aggregation_10u', query_type: 'aggregation', load_level: 10,
    mysql_avg_duration: 0.158, mysql_p95: 0.17, mysql_stddev: 0.02, mysql_count: 203,
    postgres_avg_duration: 0.299, postgres_p95: 0.31, postgres_stddev: 0.01, postgres_count: 41,
    winner: 'MySQL', difference_percent: 88.8
  },
  { schema: 'finalEmp', test_name: 'aggregation_40u', query_type: 'aggregation', load_level: 40,
    mysql_avg_duration: 0.156, mysql_p95: 0.16, mysql_stddev: 0.00, mysql_count: 280,
    postgres_avg_duration: 0.302, postgres_p95: 0.32, postgres_stddev: 0.00, postgres_count: 40,
    winner: 'MySQL', difference_percent: 94.2
  },

  // groupby
  { schema: 'finalEmp', test_name: 'groupby_10u', query_type: 'groupby', load_level: 10,
    mysql_avg_duration: 0.158, mysql_p95: 0.16, mysql_stddev: 0.02, mysql_count: 103,
    postgres_avg_duration: 0.304, postgres_p95: 0.33, postgres_stddev: 0.01, postgres_count: 13,
    winner: 'MySQL', difference_percent: 92.8
  },
  { schema: 'finalEmp', test_name: 'groupby_40u', query_type: 'groupby', load_level: 40,
    mysql_avg_duration: 0.157, mysql_p95: 0.17, mysql_stddev: 0.00, mysql_count: 156,
    postgres_avg_duration: 0.301, postgres_p95: 0.33, postgres_stddev: 0.01, postgres_count: 21,
    winner: 'MySQL', difference_percent: 92.4
  },

  // purecount
  { schema: 'finalEmp', test_name: 'purecount_10u', query_type: 'purecount', load_level: 10,
    mysql_avg_duration: 0.418, mysql_p95: 0.79, mysql_stddev: 0.23, mysql_count: 147,
    postgres_avg_duration: 0.205, postgres_p95: 0.35, postgres_stddev: 0.04, postgres_count: 28,
    winner: 'PostgreSQL', difference_percent: 103.9
  },
  { schema: 'finalEmp', test_name: 'purecount_40u', query_type: 'purecount', load_level: 40,
    mysql_avg_duration: 0.372, mysql_p95: 0.53, mysql_stddev: 0.08, mysql_count: 206,
    postgres_avg_duration: 0.210, postgres_p95: 0.27, postgres_stddev: 0.02, postgres_count: 26,
    winner: 'PostgreSQL', difference_percent: 76.8
  },
];

export default DEMO_RESULTS;
