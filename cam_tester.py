import archiver
import camera
import time

"""
Description: tests a camera, returning the number of frames that were collected.

Inputs: 'cam_id' : the ID of the camera in the SQL database
        'test_len' : the time (in seconds) that the tests should run

Output: The number of frames that could be collected from the camera within the
        test length
"""
def test_cam(cam_id, test_len):
    # save the camera, based on the camera ID
    cam = archiver.get_camera_db(cam_id, test_len, 0)

    num_frames = 0
    start_time = time.time()
    while (time.time() - start_time < test_len):
        cam.get_frame()
        num_frames += 1
    time_elapsed = time.time() - start_time
    print("{0:d} frames collected in {1:0.2f} seconds".format(num_frames,\
                                                              time_elapsed))
    return

if __name__ == '__main__':
    pass
