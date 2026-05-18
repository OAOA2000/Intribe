from app.services.posts_service import build_comment_tree


def test_build_comment_tree_keeps_nested_replies_and_deleted_placeholder():
    comments = [
        {
            "id": "root",
            "parent_id": None,
            "author_id": "u1",
            "content": "root comment",
            "deleted_at": None,
        },
        {
            "id": "child",
            "parent_id": "root",
            "author_id": "u2",
            "content": "child comment",
            "deleted_at": "2026-05-19T00:00:00+00:00",
        },
        {
            "id": "grandchild",
            "parent_id": "child",
            "author_id": "u3",
            "content": "grandchild comment",
            "deleted_at": None,
        },
    ]

    tree = build_comment_tree(comments)

    assert len(tree) == 1
    assert tree[0]["id"] == "root"
    assert tree[0]["children"][0]["id"] == "child"
    assert tree[0]["children"][0]["content"] == "该评论已删除"
    assert tree[0]["children"][0]["children"][0]["id"] == "grandchild"
