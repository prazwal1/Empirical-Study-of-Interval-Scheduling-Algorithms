from .sorting import merge_sort, merge_sort_by_duration

class EarlierStartTime:
    def __init__(self, job):
        self.job = job
    
    def schedule_jobs(self):
        self.job = merge_sort(self.job, dimension=0)
        self.selected_jobs = [self.job[0]]
        for job in self.job[1:]:
            if job[0] >= self.selected_jobs[-1][1]:
                self.selected_jobs.append(job)
        return self.selected_jobs


class EarliestFinishTime:
    def __init__(self, job):
        self.job = job
    
    def schedule_jobs(self):
        self.job = merge_sort(self.job, dimension=1)
        self.selected_jobs = [self.job[0]]
        for job in self.job[1:]:
            if job[0] >= self.selected_jobs[-1][1]:
                self.selected_jobs.append(job)
        return self.selected_jobs
    
class ShortestDuration:
    def __init__(self, job):
        self.job = job
    
    def schedule_jobs(self):
        self.job = merge_sort_by_duration(self.job)
        self.selected_jobs = [self.job[0]]
        for job in self.job[1:]:
            if job[0] >= self.selected_jobs[-1][1]:
                self.selected_jobs.append(job)
        return self.selected_jobs