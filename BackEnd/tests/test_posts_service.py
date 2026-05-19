from app.services.posts_service import build_comment_tree


def test_build_comment_tree_promotes_replies_when_parent_is_missing():
    comments = [
        {
            "id": "root",
            "parent_id": None,
            "author_id": "u1",
            "content": "root comment",
            "deleted_at": None,
        },
        {
            "id": "grandchild",
            "parent_id": "deleted-parent",
            "author_id": "u3",
            "content": "grandchild comment",
            "deleted_at": None,
        },
    ]

    tree = build_comment_tree(comments)

    assert len(tree) == 2
    assert tree[0]["id"] == "root"
    assert tree[1]["id"] == "grandchild"
