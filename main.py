import cv2
import numpy as np
import ezdxf

def detect_contours(image_paths, min_area=100):  # min_area can be adjusted as needed
    all_contours = []
    
    for image_path in image_paths:
        # Read the image and convert it to grayscale
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Convert the grayscale image to binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Detect the contours
        contours, hierarchy = cv2.findContours(binary, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

        # Filter out the largest contour and small contours by area
        largest_contour = max(contours, key=cv2.contourArea)
        filtered_contours = [cnt for cnt in contours if cnt is not largest_contour and cv2.contourArea(cnt) > min_area]

        all_contours.extend(filtered_contours)

    return all_contours

def export_contours_to_dxf(contours, dxf_path, sheet_size_feet=1.5, pixels_per_foot=426.67, spacing_feet=0.1):
    # Create a DXF document
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Convert sheet size to pixels and set initial positioning
    sheet_size_pixels = sheet_size_feet * pixels_per_foot
    x_offset = y_offset = spacing_feet  # Initial offset from the sheet edge

    for contour in contours:
        # Scale contour coordinates from pixels to feet
        scaled_contour = [
            (point[0][0] / pixels_per_foot + x_offset, point[0][1] / pixels_per_foot + y_offset) 
            for point in contour
        ]

        # Calculate contour bounding box
        contour_width = max(p[0] for p in scaled_contour) - min(p[0] for p in scaled_contour)
        contour_height = max(p[1] for p in scaled_contour) - min(p[1] for p in scaled_contour)

        # Ensure the contour fits on the sheet, move to the next row if needed
        if x_offset + contour_width > sheet_size_feet:
            x_offset = spacing_feet
            y_offset += contour_height + spacing_feet
            if y_offset + contour_height > sheet_size_feet:
                print("Warning: Contours exceed sheet size and cannot be fully nested.")
                break  # Stop if we exceed the sheet size

        # Add contour to DXF as a polyline if it has more than one point
        if len(scaled_contour) > 1:
            msp.add_lwpolyline(scaled_contour, close=True)

        # Update x_offset for the next contour to place it beside the previous one
        x_offset += contour_width + spacing_feet

    # Save the DXF file
    doc.saveas(dxf_path)
    print(f"DXF file saved successfully at: {dxf_path}")

# Example usage
image_paths = [
    "C:/Users/Arsh/Pictures/Screenshots/2.png", 
    "C:/Users/Arsh/Pictures/Screenshots/2.png", 
    "C:/Users/Arsh/Pictures/Screenshots/2.png"
]  # Input image paths
dxf_output_path = "C:/Users/Arsh/Pictures/Screenshots/output_combined.dxf"  # Output DXF file path

# Detect contours from all images
contours = detect_contours(image_paths)

# Export all contours to a single DXF file with nesting
export_contours_to_dxf(contours, dxf_output_path)
