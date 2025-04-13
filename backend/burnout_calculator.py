def calculate_burnout(steps, minutes_asleep, commits, fatigue_score):
    def normalize(val, min_val, max_val):
        return (val - min_val) / (max_val - min_val)

    def avg(arr):
        return sum(arr) / len(arr)

    sleep_norm = 1 - normalize(avg(minutes_asleep), 360, 540)
    steps_norm = 1 - normalize(avg(steps), 5000, 10000)
    commits_norm = normalize(avg(commits), 0, 15)
    fatigue_norm = normalize(fatigue_score, 1, 10)

    burnout = (
        0.40 * sleep_norm +
        0.20 * steps_norm +
        0.20 * commits_norm +
        0.20 * fatigue_norm
    )

    return round(burnout * 100, 2)
