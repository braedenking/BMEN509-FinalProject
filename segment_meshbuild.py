# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 14:53:37 2022

@author: Braeden
"""

import pydicom # Version 2.2.2
import numpy as np # 1.12.3
import matplotlib.pyplot as plt #3.4.3
import os
from skimage.filters import threshold_otsu # 0.18.3
from skimage import measure # 0.18.3
from mpl_toolkits.mplot3d.art3d import Poly3DCollection 


# Function to read DICOM files into an array
def read_files(path):
    images = []
    for filename in os.listdir(path):
        image = pydicom.read_file(os.path.join(path, filename), force='true')
        image.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        images.append(image)

    print("Succesfully read all files...")
    return images


# Fucntion to sort DICOM files numerically
def sort_dicom_array(array):
    
    for i in range(1, len(array)):
        key = array[i]
        
        j = i - 1
        while j >= 0 and key[0x20, 0x13].value < int(array[j][0x20, 0x13].value):
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key
        
    print("Succesfully sorted DICOM files numerically...")


def make_mesh(image, threshold=5, step_size=1):
    # generation of the vertices and faces of polygons using marching cubes
    verts, faces, norm, val = measure.marching_cubes_lewiner(image, step_size=step_size, allow_degenerate=True)
    print('Succesfully created vertices and faces of 3D mesh...')
    return verts, faces


def plt_3d(verts, faces, orientationX, orientationY):
 
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    x,y,z = zip(*verts) 
        
    # verts[faces] generates a collection of triangles which is needed by Poly3DCollection
    mesh = Poly3DCollection(verts[faces], linewidths=0.05, alpha=1)
    
    face_color = [0.89, 0.85, 0.79]    #bone colour
    mesh.set_facecolor(face_color)    
    mesh.set_edgecolor([0,0,0])    #black
    ax.add_collection3d(mesh)    #creates the volume image

    ax.set_xlim(0, max(x))
    ax.set_ylim(0, max(y))
    ax.set_zlim(0, max(z))
    
    ax.view_init(orientationX, orientationY)   #sets the orientation of the view
    
    plt.show() 


def write_ply(filename, points=None, faces=None):
    
    print('Writing values to .ply file...')
    
    if not filename.endswith('ply'):
        filename += '.ply'
        
    with open(filename, 'w') as ply:
        header = ['ply']
        header.append(str("format ascii 1.0"))
        
                
        if points is not None:
            header.append("element vertex " + str(len(points)))
            header.append("property float x")
            header.append("property float y")
            header.append("property float z")
            
        if faces is not None:
            faces = faces.copy()
            #faces.insert(loc=0, column="n_points", value=3)
            np.insert(faces, (0), 3, axis=1)
            faces[0, :] = faces[0, :].astype("u1")
            header.append('element face ' + str(len(faces)))
            header.append('property list uchar int vertex_indices')
        
        header.append('end_header')
        
        for line in header:
            ply.write("%s\n" % line)
            
        if points is not None:
            i = 0
            for i in range(i, len(points)):
                ply.write('{} {} {}\n'.format(str(points[i, 0]), str(points[i, 1]), str(points[i, 2])))
            #pd.DataFrame(points).to_csv(filename, sep=" ", header=False, index=False, mode='a', encoding='ascii')
       
        if faces is not None:
            i = 0
            for i in range (i, len(faces)):
                ply.write('3 {} {} {}\n'.format(str(faces[i, 0]), str(faces[i, 1]), str(faces[i, 2])))
            #pd.DataFrame(faces).to_csv(filename, sep=" ", header=False, index=False, mode='a', encoding='ascii')
           
        print('PLY file complete')
        return True


########################################
#-----------START OF SCRIPT------------#
########################################

fig = plt.figure(figsize=(12, 4), dpi=100, facecolor='w', edgecolor='b')
plt.set_cmap(plt.gray())

phalanx1_files = read_files('Data/p1') # Read DICOM files
sort_dicom_array(phalanx1_files) # Sort files numerically
pixelArray = [] # Declare array to hold images from DICOM files

# Displays 10 images from the set
# for i in range(10):
#     plt.subplot(2, 5, i + 1)
#     plt.imshow(phalanx1_files[i * 5 + 5].pixel_array, cmap='gray')

# Fill image array with cropped CT slice
for file in phalanx1_files:
    cropped_image = file.pixel_array[250:288, 225:285]
    pixelArray.append(cropped_image)
    # plt.imshow(file.pixel_array[250:288, 225:285], cmap='gray')
    # plt.show()

plt.imshow(pixelArray[5], cmap='gray')
np.asarray(pixelArray) # Convert to numpy array


# Checks to insure images are being formed properly
# for i in range(10):
#     plt.subplot(2, 5, i + 1)
#     plt.imshow(pixelArray[i * 5 + 5], cmap='gray')

#plt.show()

# Checks to insure segmentation is being performed correctly
# test_image1 = pixelArray[3]
# thresh1 = threshold_otsu(test_image1) - 350
# binary1 = test_image1 > thresh1
#
# test_image2 = pixelArray[50]
# thresh2 = threshold_otsu(test_image2)
# binary2 = test_image2 > thresh2
#
# plt.subplot(1, 2, 1)
# plt.imshow(binary1)
# plt.subplot(1, 2, 2)
# plt.imshow(test_image1)
# plt.show()

SegmentedArray3D = np.zeros((len(pixelArray), 38, 60)) # Declare array for segmented images

# Loop to segment images and append to SegmentedArray3D
i = 0
for image in pixelArray:
    thresh = 1100 #threshold_otsu(image)
    binary = image > thresh
    SegmentedArray3D[i, :, :] = binary
    i = i + 1
 
    
######-------- Image output for report images --------######
# Display segmented images
# for image in SegmentedArray3D:
#     plt.imshow(image, cmap='gray')
#     plt.show()

# plt.imshow(SegmentedArray3D[5], cmap='gray')

# fig = plt.figure(figsize=(12, 8), dpi=100, facecolor='w', edgecolor='b')
# plt.subplot(2, 2, 1)
# plt.title('Slice 9 (Original)')
# plt.imshow(pixelArray[10], cmap='gray')
# plt.subplot(2, 2, 2)
# plt.title('Slice 9 (Segmented)')
# plt.imshow(SegmentedArray3D[10], cmap='gray')
# plt.subplot(2, 2, 3)
# plt.title('Slice 24 (Original)')
# plt.imshow(pixelArray[25], cmap='gray')
# plt.subplot(2, 2, 4)
# plt.title('Slice 24 (Segmented)')
# plt.imshow(SegmentedArray3D[25], cmap='gray')

#SegmentedArray3D[:, 31, :] = 0

# Loop to display some segmented images
# for i in range(10):
#     plt.subplot(2, 5, i + 1)
#     plt.imshow(SegmentedArray3D[i * 5 + 5, :, :], cmap='gray')
######---------------------------------------------######

verts, faces = make_mesh(SegmentedArray3D, 1000) # Make array of vertices and faces
#plt_3d(verts, faces, 30, 60) # Plot 3D mesh

np.asarray(verts)
np.asarray(faces)

write_ply("p1_unedited.ply", points=verts, faces=faces)





