from app import app, db
import logging

logging.basicConfig(format='[%(name)s][%(asctime)s][%(message)s]', level=logging.INFO)

tasks_pool = list()


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


def init_background_tasks():
    from app.utils import recommendation_classes
    from app import models
    from app import RecommendationBackGroundTask

    registered_tasks = models.RecommendationItem.query.all()
    for task in registered_tasks:
        flower = models.Flower.query.filter_by(id=task.flower).first()
        if not flower:
            db.session.delete(task)
            db.session.commit()
        else:
            recommendation_class_name = task.r_class
            recommendation_class = list(filter(lambda x: x.__name__ == recommendation_class_name,
                                               recommendation_classes()))[0]

            if not any([x.t_id == task.id for x in tasks_pool]):
                tasks_pool.append(RecommendationBackGroundTask(
                    recommendation_class.create_from_db(task.id, flower)))


if __name__ == '__main__':
    # Init tasks
    init_background_tasks()
    app.run(debug=True, host='0.0.0.0')
