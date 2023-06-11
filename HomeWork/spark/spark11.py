#Spark RDD API - Task 1
import csv
import math
names = ['ID', 'Name', 'global_id', 'IsNetObject', 'OperatingCompany', 'TypeObject', 'AdmArea', 'District', 'Address', 'PublicPhone', 'SeatsCount', 'SocialPrivileges', 'Longitude_WGS84', 'Latitude_WGS84', 'geoData']
def calculate_distance(lat1, lng1, lat2, lng2):
    # Dealing with radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)

    radius = 6371
    delta_lat = lat2_rad - lat1_rad
    delta_lng = lng2_rad - lng1_rad

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = radius * c

    return distance

def task():
    with open('./data/places.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)

        points = []
        targetDistances = []
        distance_between = []

        # Task point
        target_lat = 55.751244
        target_lng = 37.618423

        for row in reader:
            name, lat, lng = row[1], float(row[12]), float(row[13])
            points.append((name, lat, lng))

        # distance between point and cafes. First 10
        for i in range (len(points)):
            distance = calculate_distance(target_lat, target_lng, points[i][1], points[i][2])
            targetDistances.append((points[i][0], distance))
            # Выводим только первые 10
            if i <= 10:
                print(f"{targetDistances[i]} km")

        # Distance between all cafes
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                name1, lat1, lng1 = points[i]
                name2, lat2, lng2 = points[j]
                distance = calculate_distance(lat1, lng1, lat2, lng2)
                distance_between.append((name1, name2, distance))
                
        # First 10
        print("Distance between firts 10:")
        for name1, name2, distance in distance_between[:10]:
            print(f"{name1} - {name2}: {distance} km")       

        # Sorting for closest and farest
        distance_between.sort(key=lambda x: x[2])

        print("Top 10 closest:")
        for name1, name2, distance in distance_between[:10]:
            print(f"{name1} - {name2}: {distance} km")

        print("Top 10 farest:")
        for name1, name2, distance in distance_between[-10:]:
            print(f"{name1} - {name2}: {distance} km")

if __name__ == '__main__':
    task()