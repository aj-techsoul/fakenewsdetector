from database_models import db
from database_models.notification import Notification

def create_user_notification(user_id, title, message, type='info'):
    """
    Save a new notification log in the database.
    """
    if not user_id:
        return None
        
    try:
        new_notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        db.session.add(new_notif)
        db.session.commit()
        return new_notif
    except Exception as e:
        db.session.rollback()
        print(f"Notification error: {e}")
        return None


def get_user_notifications(user_id, only_unread=False):
    """
    Retrieve notification list for a user.
    """
    query = Notification.query.filter_by(user_id=user_id)
    if only_unread:
        query = query.filter_by(is_read=False)
        
    return query.order_by(Notification.created_at.desc()).all()


def mark_notifications_read(user_id):
    """
    Mark all notifications as read for a user.
    """
    try:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error marking read: {e}")
        return False
