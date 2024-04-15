from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from recipes.utils import is_number
from users.models import Follow, User


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get('request').user
        return user.is_authenticated and user.follow.filter(
            following=obj
        ).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}


class RecipeForFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта в FollowSerializer."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки/отписки."""

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Нельзя подписаться на одного пользователя дважды'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        following = data.get('following')
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя'
            )
        return data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписок."""

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = UserSerializer.Meta.fields + ('recipes', 'recipe_count',)

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get('request').user
        return user.is_authenticated and user.follow.filter(
            following=obj.following
        ).exists()

    def get_recipes(self, obj):
        """"Список рецептов."""
        recipes = Recipe.objects.filter(author=obj.following)
        request = self.context.get('request')
        context = {'request': request}
        limit = request.GET.get('recipes_limit')
        if limit:
            if is_number(limit):
                recipes = recipes[:int(limit)]
        return RecipeForFollowSerializer(
            recipes, many=True, context=context
        ).data

    def get_recipes_count(self, obj):
        """Колличество рецептов."""
        return obj.following.recipes.count()
