import client from './client';

export const fairnessApi = {
  auditFairness: (jobId = null, groupKey = 'group', scoreKey = 'overall_score', threshold = 10.0) => {
    return client.post('/fairness/audit', {
      job_id: jobId,
      group_key: groupKey,
      score_key: scoreKey,
      threshold: threshold
    });
  }
};

