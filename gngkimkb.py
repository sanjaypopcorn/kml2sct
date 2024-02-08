import struct

# Binary data
f = open("delhiFIR.bin", mode="rb")
 
# Reading file data with read() method

binary_data = f.read()
print(binary_data)

# Unpack the unsigned 32-bit integer (number of points)
num_points = struct.unpack('>I', binary_data[:4])[0]

# Unpack the single-precision floating-point number pairs for lon/lat
lon_lat_pairs = struct.unpack('>' + 'ff' * num_points, binary_data[4:])

# Format lon/lat pairs into text
lon_lat_text = '\n'.join(f'{lon},{lat}' for lon, lat in zip(lon_lat_pairs[::2], lon_lat_pairs[1::2]))

print(f'Number of points: {num_points}')
print('Longitude, Latitude:')
print(lon_lat_text)