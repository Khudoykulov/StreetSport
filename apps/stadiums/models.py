from django.db import models
from apps.account.models import User
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_save


class Stadium(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    description = models.TextField(null=True, blank=True, verbose_name="Tavsif")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stadiums', verbose_name="Egasi")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_stadiums',
                                verbose_name="Menejer")
    views = models.PositiveIntegerField(default=0, verbose_name="Ko‘rishlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    modified_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        if user is not None:
            if user.role not in ['admin', 'owner']:
                raise PermissionDenied("Sizga ushbu amalni bajarishga ruxsat yo‘q.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = Rating.objects.filter(stadium=self)
        return sum(rating.rank for rating in ratings) / ratings.count() if ratings else 0


class StadiumLocation(models.Model):
    stadium = models.OneToOneField(Stadium, on_delete=models.CASCADE, related_name='location', verbose_name="Stadion")
    address = models.CharField(max_length=200, verbose_name="Manzil")
    latitude = models.CharField(max_length=50, null=True, blank=True, verbose_name="Kenglik")
    longitude = models.CharField(max_length=50, null=True, blank=True, verbose_name="Uzunlik")

    def __str__(self):
        return f"{self.stadium.name} manzili"


# Stadion rasmlari
class StadiumImage(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='images', verbose_name="Stadion")
    image = models.ImageField(upload_to='stadiums/', verbose_name="Rasm")

    def __str__(self):
        return f"{self.stadium.name} rasmi"


class Rating(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='ratings', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    rank = models.PositiveSmallIntegerField(default=0, choices=[(i, i) for i in range(1, 11)], verbose_name="Baho")

    def __str__(self):
        return f"{self.stadium.name} - {self.rank}"


class Like(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='likes', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} liked {self.stadium.name}"


class Wishlist(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} wishlisted {self.stadium.name}"


class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    product = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    top_level_comment_id = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} (pid: {self.product.id} -> cid: {self.id})'

    @property
    def tree(self):
        return Comment.objects.filter(top_level_comment_id=self.id)


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='comment/')


def comment_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.parent:
            # reply
            instance.top_level_comment_id = instance.parent.top_level_comment_id
        else:
            instance.top_level_comment_id = instance.id
        instance.save()


post_save.connect(comment_post_save, sender=Comment)
