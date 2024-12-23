async def notify(owner, repo, url, priority="low"):
    try:
        if priority == "high":
            # Try Twitter first
            await tweet_notification(owner, repo, url)
        else:
            # Default to email
            await email_notification(owner, repo, url)
    except TweepyException as e:
        # Fallback to email if Twitter fails
        print(f"Twitter notification failed, falling back to email: {e}")
        await email_notification(owner, repo, url) 