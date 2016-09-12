
def analyse_conf(conf):
    total_q = len(conf.questions.all())
    written_q = [q for q in conf.questions.all() if q.question]
    valid_q = [q for q in written_q
               if len([a for a in q.answers.all() if a.answer and a.correct]) >= 1
               and len([a for a in q.answers.all() if a.answer ]) == 5
               ]
    """ valid question mean question with a valid answer """
    progress = len(valid_q) / total_q * 100
    return {
        'total_q': total_q,
        'written_q': [q.id for q in written_q],
        'valid_q': [q.id for q in valid_q],
        'progress': progress,
    }
