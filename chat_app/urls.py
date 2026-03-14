from django.urls import path
from .views import (
    GroupMessagesView,
    CreateGroupView,
    GroupMemberView,
    DirectThreadView,
    DirectMessagesView,
    SearchUsersView,
)


urlpatterns = [
    # Group
    path('groups/create/',                              CreateGroupView.as_view(),   name='create_group'),
    path('groups/<int:group_id>/messages/',             GroupMessagesView.as_view(), name='group_messages'),
    path('groups/<int:group_id>/members/<str:action>/', GroupMemberView.as_view(),   name='group_member'),

    # Direct
    path('direct/<int:user_id>/thread/',               DirectThreadView.as_view(),    name='get_or_create_direct_thread'),
    path('direct/<int:thread_id>/messages/',           DirectMessagesView.as_view(),  name='direct_messages'),

    # Utility
    path('users/search/',                              SearchUsersView.as_view(),     name='search_users'),
]