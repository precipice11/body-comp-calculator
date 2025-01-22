from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.http import HttpResponse
from django import forms

# Create your views here.

class Details(forms.Form):
    currentWeight = forms.DecimalField(label="Current Weight")
    currentBF = forms.DecimalField(label="Current BF")
    goalBF = forms.DecimalField(label="Goal BF")
    calorieDeficit = forms.IntegerField(label="Daily Calorie Deficit")


def index(request):
    return render(request, "webapp/index.html", {
        "form": Details()
    })

# Add view to handle calculations and display results
def add(request):
    if request.method == "POST":
        form = Details(request.POST)
        if form.is_valid():
            # Extract cleaned data
            current_weight = form.cleaned_data["currentWeight"]
            current_bf = form.cleaned_data["currentBF"] / 100  # Convert percentage to decimal
            goal_bf = form.cleaned_data["goalBF"] / 100  # Convert percentage to decimal
            calorie_deficit = form.cleaned_data["calorieDeficit"]
            
            # Calculate body composition details
            body_fat = current_weight * current_bf
            lean_body_mass = current_weight - body_fat
            goal_body_weight = lean_body_mass / (1 - goal_bf)
            calories_to_burn = (current_weight - goal_body_weight) * 7700
            days_to_goal = calories_to_burn / calorie_deficit

            # Weekly progress calculation
            weekly_data = []
            total_weight_loss = current_weight - goal_body_weight
            weekly_weight_loss = total_weight_loss / (days_to_goal / 7)
            total_bf_loss = current_bf - goal_bf
            weekly_bf_loss = total_bf_loss / (days_to_goal / 7)
            current_date = datetime.now()

            for i in range(1, int(days_to_goal // 7) + 1):
                week_date = current_date + timedelta(weeks=i)
                estimated_weight = current_weight - (weekly_weight_loss * i)
                estimated_bf = current_bf - (weekly_bf_loss * i)
                weekly_data.append({
                    "week": i,
                    "date": week_date.strftime("%d %B"),
                    "weight": round(estimated_weight, 2),
                    "body_fat": round(estimated_bf * 100, 2),
                })

            # Render results
            return render(request, "webapp/results.html", {
                "current_weight": current_weight,
                "current_bf": current_bf * 100,
                "goal_bf": goal_bf * 100,
                "goal_weight": round(goal_body_weight, 2),
                "days_to_goal": round(days_to_goal, 2),
                "weekly_data": weekly_data,
            })
    else:
        return redirect("index")