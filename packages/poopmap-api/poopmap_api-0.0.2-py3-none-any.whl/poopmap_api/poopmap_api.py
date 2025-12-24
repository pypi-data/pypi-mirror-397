from typing import Optional
import requests

class PoopmapRequestException(Exception):
    pass

class PoopmapAPI:
    """
    An unofficial Python wrapper for the Poopmap API.

    It is advised to use the `PoopmapAPI.login_with_password` method to create an instance of this class.
    But if you know your authentication_token already, you can create it directly.
    """

    base_api_endpoint = "https://api.poopmap.net/api/v1"
    host = "api.poopmap.net"
    user_agent = "Dart/2.14 (dart:io)"

    def __init__(self, authentication_token: str):
        self.authentication_token = authentication_token
        self.full_device_response: Optional[dict] = None
        self.full_session_response: Optional[dict] = None

    @staticmethod
    def login_with_password(username: str, password: str) -> 'PoopmapAPI':
        """
        Login to the Poopmap API with a username and password.

        :param username: The username of the account to login with.
        :param password: The password of the account to login with.
        :return: A `PoopmapAPI` instance.
        """
        # Get a device id and token
        devices_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/devices",
            headers={
                "accept-encoding": "gzip",
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if devices_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get a device id with error code: {devices_response.status_code}" \
                f"\n Are you sure you can reach the internet / Poopmap?"
            )

        authentication_token = devices_response.json()["device"]["token"]

        # Authenticate the device with the username and password
        sessions_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/sessions",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + authentication_token,
                "content-type": "application/json; charset=utf-8",
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            },
            json={
                "user": {
                    "username": username, 
                    "password": password
                }
            }
        )
        if sessions_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get an authentication token with error code: {sessions_response.status_code}" \
                f"\n This is probably because the username or password is incorrect."
            )
    
        # Return a new instance of the PoopmapAPI class
        poopmap_api_instance = PoopmapAPI(authentication_token=authentication_token)
        poopmap_api_instance.full_device_response = devices_response.json()
        poopmap_api_instance.full_session_response = sessions_response.json()
        return poopmap_api_instance
    
    def get_feed(self) -> dict:
        """
        Get the feed of the logged in user.

        :return: A dictionary containing the feed with the following structure:
        {
            "user": {
                "username": <string>,
                "id": <int>,
                "avatar": <null>,
                "show_map_selfies_in_feed": <bool>,
                "show_compact_feed": <bool>
            },
            "poops": [
                {
                    "id": <int>,
                    "note": <string>,
                    "place": <string>,
                    "rating": <int>,
                    "created_at": <string>,
                    "comments_count": <int>,
                    "sticker": <string>,
                    "user_id": <int>,
                    "show_location": <bool>,
                    "latitude": <float>,
                    "longitude": <float>,
                    "original_latitude": <null>,
                    "original_longitude": <null>,
                    "liked_by_you": <bool>,
                    "username": <string>,
                    "pin_color": <string>,
                    "followers_count": <int>,
                    "photos": [
                        <string>,
                        ...
                    ],
                    "photos_full": [
                        {
                            "url": <string>,
                            "width": <int>,
                            "height": <int>
                        }
                    ],
                    "avatar": <null>
                },
                ...
            ]
        }            
        """
        feed_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/feed",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if feed_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the feed with error code: {feed_response.status_code}"
            )

        return feed_response.json()
    
    def get_leagues(self) -> dict:
        """
        Get the leagues of the logged in user.

        :return: A dictionary containing the leagues with the following structure:
        {
            "leagues": [
                {
                    "id": <int>,
                    "active_from": <null>,
                    "active_to": <null>,
                    "chat_enabled": <bool>,
                    "created_at": <string>,
                    "current_user_rank": <int>,
                    "is_public": <bool>,
                    "join_code": <string>,
                    "league_comments_count": <int>,
                    "name": <string>,
                    "participants": <int>,
                    "score_type": <string>,
                    "username": <string>
                },
                ...
            ]
        }
        """
        leagues_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/leagues",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if leagues_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the leagues with error code: {leagues_response.status_code}"
            )
        
        return leagues_response.json()
    
    def get_leagues_joinable(self) -> dict:
        """
        Get all the joinable leagues.

        :return: A dictionary containing the joinable leagues with the same structure as "get_leagues":
        {
            "leagues": [
                {
                    "id": <int>,
                    "active_from": <null>,
                    "active_to": <null>,
                    "chat_enabled": <bool>,
                    "created_at": <string>,
                    "current_user_rank": <null>,
                    "is_public": <bool>,
                    "join_code": <string>,
                    "league_comments_count": <int>,
                    "name": <string>,
                    "participants": <int>,
                    "score_type": <string>,
                    "username": <string>
                },
                ...
            ]
        }
        """
        leagues_joinable_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/leagues/joinable",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if leagues_joinable_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the joinable leagues with error code: {leagues_joinable_response.status_code}"
            )
        
        return leagues_joinable_response.json()

    def post_join_league(self, league_id: int) -> dict:
        """
        Join the league with the given id.

        :param league_id: The id of the league to join.
        :return: A dictionary containing the league with the following structure:
        {
            "id": <int>,
            "name": <string>,
            "is_public": <bool>,
            "join_code": <string>,
            "user_id": <int>,
            "active_from": <null>,
            "active_to": <null>,
            "created_at": <string>,
            "updated_at": <string>,
            "league_participants_count": <int>,
            "score_type": <string>,
            "league_comments_count": <int>,
            "chat_enabled": <bool>,
            "deleted_at": <null>,
            "is_official": <bool>,
        }
        """
        join_league_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/leagues/" + str(league_id) + "/join",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if join_league_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to join the league with error code: {join_league_response.status_code}"
            )
        
        return join_league_response.json()

    def get_notifications(self) -> dict:
        """
        Get the notifications of the logged in user.
        
        The app uses this request every minute to check for new notifications.
        So to avoid looking suspicious, you should probably do the same.
        
        :return: A dictionary containing the notifications with the following structure:
        {
            "notifications": [
                {
                    "id": <int>,
                    "type": <string>,
                    "params": {
                        "poop_id": <int>,
                        "poop_time": <string>,
                        "poop_username": <string>
                    },
                    "created_at": <string>
                },
                ...
            ]
        }
        """
        notifications_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/notifications",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if notifications_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the notifications with error code: {notifications_response.status_code}"
            )
        
        return notifications_response.json()
    
    def get_poop_post(self, poop_id: int) -> dict:
        """
        Get the poop post with the given id.

        :param poop_id: The id of the poop post.
        :return: A dictionary containing the poop post with the following structure:
        {
            poop: {
                id: <int>,
                latitude: <float>,
                longitude: <float>,
                note: <string>,
                place: <string>,
                rating: <int>,
                created_at: <string>,
                username: <string>,
                user_id: <int>,
                followers_count: <int>,
                liked_by_you: <int>,
                pin_color: <null>,
                comments_count: <int>,
                photos: [
                    <string>
                ],
                photos_full: [
                    {
                        url: <string>,
                        width: <int>,
                        height: <int>
                    }
                ],
                device: {
                    id: <int>
                }
            }
        }
        """
        poop_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/poops/" + str(poop_id),
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the poop with error code: {poop_response.status_code}"
            )
        
        return poop_response.json()
    
    def get_poop_comments(self, poop_id: int) -> dict:
        """
        Get the comments on a poop post.

        :param poop_id: The id of the poop post.
        :return: A dictionary containing the comments with the following structure:
        {
            comments: [
                {
                    id: <int>,
                    created_at: <string>,
                    username: <string>,
                    comment: <string>,
                    avatar: <null>,
                    user_id: <int>,
                    photo: <null>,
                    giphy: <null>
                },
                ...
            ]
        }
        """
        poop_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/poops/" + str(poop_id) + "/comments",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the poop comments with error code: {poop_response.status_code}"
            )
        
        return poop_response.json()
    
    def get_poop_likes(self, poop_id: int) -> dict:
        """
        Get the users the liked the given poop post.

        :param poop_id: The id of the poop post.
        :return: A dictionary containing the users that liked the given poop post with the following structure:
        {
            users: [
                {
                    id: <int>,
                    avatar: <null>,
                    pin_color: <null>,
                    poops_count: <int>,
                    username: <string>
                },
                ...
            ]
        }
        """
        poop_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/poops/" + str(poop_id) + "/likes",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )

        if poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get the poop likes with error code: {poop_response.status_code}"
            )
        
        return poop_response.json()

    def post_create_poop(self, latitude: float, longitude: float, note: str, place: str, rating: int) -> dict:
        """
        Create a new poop post.

        :param latitude: The latitude of the poop post.
        :param longitude: The longitude of the poop post.
        :param note: The note of the poop post.
        :param place: The place of the poop post.
        :param rating: The rating of the poop post.
        :return: A dictionary containing the created poop post with the same structure as "get_poop_post".
        {
            poop: {
                id: <int>,
                latitude: <float>,
                longitude: <float>,
                original_latitude: <null>,
                original_longitude: <null>,
                note: <string>,
                place: <string>,
                rating: <int>,
                rating_float: <float>,
                created_at: <string>,
                username: <string>,
                user_id: <int>,
                followers_count: <int>,
                pin_color: <null>,
                comments_count: <int>,
                nearby_places: [],
                sticker: <null>,
                device: {
                    id: <int>
                }
            }
        }
        """
        create_poop_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/poops",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={
            "poop": {
                "latitude": latitude,
                "longitude": longitude,
                "note": note,
                "place": place,
                "rating": rating
            }
            }
        )
        if create_poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to create the poop with error code: {create_poop_response.status_code}"
            )
        return create_poop_response.json()

    def post_create_comment(self, poop_id: int, comment: str) -> dict:
        """
        Create a comment on a poop post.

        :param poop_id: The id of the poop post.
        :param comment: The comment text.
        :return: A dictionary containing the created comment.
        {
            comment: {
                id: <int>,
                created_at: <string>,
                username: <string>,
                comment: <string>,
                avatar: <null>,
                user_id: <int>,
                photo: <null>,
                giphy: <null>
            }
        }
        """
        create_comment_response = requests.post(
            PoopmapAPI.base_api_endpoint + f"/poops/{poop_id}/comments.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"comment": {"comment": comment}}
        )
        if create_comment_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to create the comment with error code: {create_comment_response.status_code}"
            )
        return create_comment_response.json()

    def delete_comment(self, poop_id: int, comment_id: int) -> dict:
        """
        Delete a comment from a poop post.

        :param poop_id: The id of the poop post.
        :param comment_id: The id of the comment to delete.
        :return: A dictionary (usually empty) if successful.
        """
        delete_comment_response = requests.delete(
            PoopmapAPI.base_api_endpoint + f"/poops/{poop_id}/comments/{comment_id}",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/x-www-form-urlencoded"
            }
        )
        if delete_comment_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to delete the comment with error code: {delete_comment_response.status_code}"
            )
        return delete_comment_response.json()

    def delete_following(self, user_id: int) -> dict:
        """
        Delete a following.

        :param user_id: The id of the user to unfollow.
        :return: A dictionary (usually empty) if successful.
        """
        delete_following_response = requests.delete(
            PoopmapAPI.base_api_endpoint + "/followings.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"user": {"id": user_id}}
        )
        if delete_following_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to delete following with error code: {delete_following_response.status_code}"
            )
        return delete_following_response.json()

    def delete_league(self, league_id: int) -> dict:
        """
        Delete a league.

        :param league_id: The id of the league to delete.
        :return: A dictionary (usually empty) if successful.
        """
        delete_league_response = requests.delete(
            PoopmapAPI.base_api_endpoint + f"/leagues/{league_id}",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/x-www-form-urlencoded"
            }
        )
        if delete_league_response.status_code not in [200, 204]:
            raise PoopmapRequestException(
                f"Request failed to delete league with error code: {delete_league_response.status_code}"
            )
        return delete_league_response.json() if delete_league_response.content else {}

    def delete_leave_league(self, league_id: int) -> dict:
        """
        Leave a league.

        :param league_id: The id of the league to leave.
        :return: A dictionary (usually empty) if successful.
        """
        leave_league_response = requests.delete(
            PoopmapAPI.base_api_endpoint + f"/leagues/{league_id}/leave",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/x-www-form-urlencoded"
            }
        )
        if leave_league_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to leave league with error code: {leave_league_response.status_code}"
            )
        return leave_league_response.json()

    def delete_poop(self, poop_id: int) -> dict:
        """
        Delete a poop post.

        :param poop_id: The id of the poop post to delete.
        :return: A dictionary (usually empty) if successful.
        """
        delete_poop_response = requests.delete(
            PoopmapAPI.base_api_endpoint + f"/poops/{poop_id}.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            }
        )
        if delete_poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to delete poop with error code: {delete_poop_response.status_code}"
            )
        return delete_poop_response.json()

    def get_followers(self, user_id: int) -> dict:
        """
        Get followers for a user.

        :param user_id: The id of the user.
        :return: A dictionary containing the user's followers.
        """
        get_followers_response = requests.get(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}/followers",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_followers_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get followers with error code: {get_followers_response.status_code}"
            )
        return get_followers_response.json()

    def get_followings(self, user_id: int) -> dict:
        """
        Get followings for a user.

        :param user_id: The id of the user.
        :return: A dictionary containing the user's followings.
        """
        get_followings_response = requests.get(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}/followings",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_followings_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get followings with error code: {get_followings_response.status_code}"
            )
        return get_followings_response.json()

    def get_me_poops(self) -> dict:
        """
        Get poops for the authenticated user.

        :return: A dictionary containing the user's poops.
        """
        get_me_poops_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/me/poops",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_me_poops_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get me poops with error code: {get_me_poops_response.status_code}"
            )
        return get_me_poops_response.json()

    def get_poops(self) -> dict:
        """
        Get all poops for the logged in user.

        :return: A dictionary containing all poops for the user.
        """
        get_poops_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/poops",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_poops_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get poops with error code: {get_poops_response.status_code}"
            )
        return get_poops_response.json()

    def get_user(self, user_id: int) -> dict:
        """
        Get a user by id.

        :param user_id: The id of the user.
        :return: A dictionary containing the user's details.
        """
        get_user_response = requests.get(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_user_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get user with error code: {get_user_response.status_code}"
            )
        return get_user_response.json()

    def get_user_badges(self, user_id: int) -> dict:
        """
        Get badges for a user.

        :param user_id: The id of the user.
        :return: A dictionary containing the user's badges.
        """
        get_user_badges_response = requests.get(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}/badges",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_user_badges_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get user badges with error code: {get_user_badges_response.status_code}"
            )
        return get_user_badges_response.json()

    def get_user_stats(self, user_id: int) -> dict:
        """
        Get stats for a user.

        :param user_id: The id of the user.
        :return: A dictionary containing the user's stats.
        """
        get_user_stats_response = requests.get(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}/stats",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_user_stats_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get user stats with error code: {get_user_stats_response.status_code}"
            )
        return get_user_stats_response.json()

    def get_users(self) -> dict:
        """
        Get all users.

        :return: A dictionary containing all users.
        """
        get_users_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/users",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_users_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get users with error code: {get_users_response.status_code}"
            )
        return get_users_response.json()

    def get_world_poops(self) -> dict:
        """
        Get world poops.

        :return: A dictionary containing world poops.
        {
            user: {
                username: <string>,
                id: <int>
            },
            poops: [
                {
                    id: <int>,
                    created_at: <string>,
                    latitude: <float>,
                    longitude: <float>,
                    name: <string>,
                    note: <string>,
                    pin_color: <null>,
                    place: <string>,
                    rating: <null>,
                    rating_float: <null>,
                    sticker: <string>,
                    user_id: <int>,
                    username: <string>
                },
                ...
            ]
        }
        """
        get_world_poops_response = requests.get(
            PoopmapAPI.base_api_endpoint + "/world",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if get_world_poops_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to get world poops with error code: {get_world_poops_response.status_code}"
            )
        return get_world_poops_response.json()

    def post_create_device(self) -> dict:
        """
        Create a device.

        :return: A dictionary containing the created device.
        """
        create_device_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/devices",
            headers={
                "accept-encoding": "gzip",
                "content-type": "application/x-www-form-urlencoded",
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            }
        )
        if create_device_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to create device with error code: {create_device_response.status_code}"
            )
        return create_device_response.json()

    def post_create_following(self, user_id: int) -> dict:
        """
        Create a following.

        :param user_id: The id of the user to follow.
        :return: A dictionary (usually empty) if successful.
        """
        create_following_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/followings.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"user": {"id": user_id}}
        )
        if create_following_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to create following with error code: {create_following_response.status_code}"
            )
        return create_following_response.json()

    def post_create_league(self, name: str, is_public: bool, join_code: str) -> dict:
        """
        Create a new league.

        :param name: The name of the league.
        :param is_public: Whether the league is public.
        :param join_code: The join code for the league.
        :return: A dictionary containing the created league.
        """
        create_league_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/leagues.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"league": {"name": name, "is_public": is_public, "join_code": join_code}}
        )
        if create_league_response.status_code not in [200, 201]:
            raise PoopmapRequestException(
                f"Request failed to create league with error code: {create_league_response.status_code}"
            )
        return create_league_response.json()

    def post_create_user(self, username: str, email: str, password: str, password_confirmation: str) -> dict:
        """
        Create a user.

        :param username: The username for the new user.
        :param email: The email for the new user.
        :param password: The password for the new user.
        :param password_confirmation: The password confirmation.
        :return: A dictionary containing the created user.
        """
        create_user_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/users.json",
            headers={
                "accept-encoding": "gzip",
                "content-type": "application/json",
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            },
            json={"user": {
                "username": username,
                "email": email,
                "password": password,
                "password_confirmation": password_confirmation
            }}
        )
        if create_user_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to create user with error code: {create_user_response.status_code}"
            )
        return create_user_response.json()

    def post_join_league_by_code(self, join_code: str) -> dict:
        """
        Join a private league by code.

        :param join_code: The join code for the league.
        :return: A dictionary containing the joined league.
        """
        join_league_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/leagues/join_by_code.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"join_code": join_code}
        )
        if join_league_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to join league by code with error code: {join_league_response.status_code}"
            )
        return join_league_response.json()

    def post_join_league_json(self, league_id: int) -> dict:
        """
        Join a public league.

        :param league_id: The id of the league to join.
        :return: A dictionary containing the joined league.
        """
        join_league_response = requests.post(
            PoopmapAPI.base_api_endpoint + f"/leagues/{league_id}/join.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            }
        )
        if join_league_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to join public league with error code: {join_league_response.status_code}"
            )
        return join_league_response.json()

    def post_like_poop(self, poop_id: int) -> dict:
        """
        Like a poop post.

        :param poop_id: The id of the poop post to like.
        :return: A dictionary (usually empty) if successful.
        """
        like_poop_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/poops/like.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"id": poop_id}
        )
        if like_poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to like poop with error code: {like_poop_response.status_code}"
            )
        return like_poop_response.json()

    def post_unlike_poop(self, poop_id: int) -> dict:
        """
        Unlike a poop post.

        :param poop_id: The id of the poop post to unlike.
        :return: A dictionary (usually empty) if successful.
        """
        unlike_poop_response = requests.post(
            PoopmapAPI.base_api_endpoint + "/poops/unlike.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"id": poop_id}
        )
        if unlike_poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to unlike poop with error code: {unlike_poop_response.status_code}"
            )
        return unlike_poop_response.json()

    def put_update_league(self, league_id: int, is_public: bool) -> dict:
        """
        Update a league.

        :param league_id: The id of the league to update.
        :param is_public: Whether the league is public.
        :return: A dictionary containing the updated league.
        """
        update_league_response = requests.put(
            PoopmapAPI.base_api_endpoint + f"/leagues/{league_id}.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"league": {"is_public": is_public}}
        )
        if update_league_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to update league with error code: {update_league_response.status_code}"
            )
        return update_league_response.json()

    def put_update_poop(self, poop_id: int, note: str, rating: int, place: str) -> dict:
        """
        Update a poop post.

        :param poop_id: The id of the poop post.
        :param note: The note of the poop post.
        :param rating: The rating of the poop post.
        :param place: The place of the poop post.
        :return: A dictionary containing the updated poop post.
        """
        update_poop_response = requests.put(
            PoopmapAPI.base_api_endpoint + f"/poops/{poop_id}.json",
            headers={
                "accept-encoding": "gzip",
                "authorization": "Token " + self.authentication_token,
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
                "content-type": "application/json"
            },
            json={"poop": {"note": note, "rating": rating, "place": place}}
        )
        if update_poop_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to update poop with error code: {update_poop_response.status_code}"
            )
        return update_poop_response.json()

    def put_update_user(self, user_id: int, **kwargs) -> dict:
        """
        Update a user.

        :param user_id: The id of the user to update.
        :param kwargs: Fields to update for the user.
        :return: A dictionary containing the updated user.
        """
        update_user_response = requests.put(
            PoopmapAPI.base_api_endpoint + f"/users/{user_id}.json",
            headers={
                "accept-encoding": "gzip",
                "content-type": "application/json",
                "host": PoopmapAPI.host,
                "user-agent": PoopmapAPI.user_agent,
            },
            json={"user": kwargs}
        )
        if update_user_response.status_code != 200:
            raise PoopmapRequestException(
                f"Request failed to update user with error code: {update_user_response.status_code}"
            )
        return update_user_response.json()
