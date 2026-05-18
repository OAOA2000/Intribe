from ..utils.validators import require_fields


def generate_activity_copy(data):
    require_fields(data, ("title",))
    title = data.get("title")
    description = data.get("description") or "精彩校园活动"
    location = data.get("location") or "校园内"
    start_time = data.get("start_time") or data.get("time") or "近期"

    copy = (
        f"欢迎参加{title}！{description}。活动将在{start_time}于{location}举行，"
        "期待和同学们一起交流、协作、碰撞灵感。快来报名加入吧！"
    )
    return {"copy": copy}
