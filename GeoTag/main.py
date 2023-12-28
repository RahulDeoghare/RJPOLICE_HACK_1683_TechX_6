import tkinter as tk
from tkinter import filedialog
from PIL import Image
from geopy.geocoders import Nominatim

class GeoTaggedCameraSystem:
    def __init__(self):
        self.cameras = {}

    def add_camera(self, name, location, specifications, owner_contact, visibility_range):
        self.cameras[name] = {
            "location": location,
            "specifications": specifications,
            "owner_contact": owner_contact,
            "visibility_range": visibility_range
        }

    def geo_tag_cameras(self, image_path, camera_name):
        geolocator = Nominatim(user_agent="geo_tagger")

        try:
            image = Image.open(image_path)
            exif_data = image._getexif()

            if exif_data and 0x8825 in exif_data:
                gps_info = exif_data[0x8825]
                
                latitude = gps_info[2][0] + gps_info[2][1]/60 + gps_info[2][2]/3600
                longitude = gps_info[4][0] + gps_info[4][1]/60 + gps_info[4][2]/3600
                
                if gps_info[3] == 'S':
                    latitude = -latitude
                if gps_info[1] == 'W':
                    longitude = -longitude

                location = geolocator.reverse((latitude, longitude), language="en")
                if location:
                    location_str = location.address
                    print(f"Location: {location_str} ({latitude}, {longitude})")

                    self.add_camera(camera_name, location_str, "Unknown", "Unknown", "Unknown")

                    self.cameras[camera_name]["latitude"] = latitude
                    self.cameras[camera_name]["longitude"] = longitude
                else:
                    print("Error: Unable to obtain location information from geocoding.")
            else:
                print("Error: Image does not contain geolocation information.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def display_camera_info(self):
        info_window = tk.Tk()
        info_window.title("Camera Information")

        canvas = tk.Canvas(info_window, width=400, height=300)
        canvas.pack()

        frame = tk.Frame(canvas)
        frame.pack()

        label = tk.Label(frame, text="Camera Information", font=("Arial", 16))
        label.pack()

        info_text = tk.Text(frame, height=10, width=50)
        info_text.pack()

        for camera, data in self.cameras.items():
            info = f"Camera: {camera}\nLocation: {data['location']} ({data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')})\nSpecifications: {data['specifications']}\nOwner Contact: {data['owner_contact']}\nVisibility Range: {data['visibility_range']}\n\n"
            info_text.insert(tk.END, info)

        scroll = tk.Scrollbar(frame, command=info_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        info_text.config(yscrollcommand=scroll.set)

        info_window.mainloop()

    def get_camera_name(self, image_path):
        root = tk.Tk()
        root.title("Enter Camera Name")

        label = tk.Label(root, text="Enter Camera Name:", font=("Arial", 12))
        label.pack(pady=10)

        entry = tk.Entry(root, font=("Arial", 12))
        entry.pack(pady=5)

        def save_name():
            camera_name = entry.get()
            self.geo_tag_cameras(image_path, camera_name)
            self.display_camera_info()
            root.destroy()

        save_button = tk.Button(root, text="Save", command=save_name, font=("Arial", 12))
        save_button.pack(pady=10)

        root.mainloop()

    def browse_image(self):
        file_path = filedialog.askopenfilename()
        self.get_camera_name(file_path)

    def create_gui(self):
        root = tk.Tk()
        root.title("Geo-Tagged Camera System")

        label = tk.Label(root, text="Select an image to geo-tag cameras:", font=("Arial", 14))
        label.pack(pady=20)

        browse_button = tk.Button(root, text="Browse Image", command=self.browse_image, font=("Arial", 12))
        browse_button.pack(pady=10)

        root.mainloop()

if __name__ == "__main__":
    camera_system = GeoTaggedCameraSystem()
    camera_system.create_gui()

