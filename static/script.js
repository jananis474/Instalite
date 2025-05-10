function likePost(postId) {
    fetch('/like/' + postId, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); // Reload page to update like count
            }
        });
}

function followUser(userId) {
    fetch('/follow/' + userId, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); // Reload page to update follow status
            }
        });
}