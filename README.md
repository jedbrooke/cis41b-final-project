# Python Image Fetcher and Reviewer (PIFAR)
This is our repository for our python final project
we are going to get an A

# Background
Machine learning requires a clean data set. For image classification tasks, a dataset can be developed by gathering images online from an image hosting service. We chose to use Imgur as the main source because its images vary heavily in quality. This raises the need to clean the dataset after collection.

Our application allows the user locally to gather images by tag or category, clean up that dataset, and send it off to a (currently local and hypothetical) server for training.

# GUI Usage
To start, run `client.py`. Click on `Search` to open a window to query images. Enter a search string and a number of images to download. A thumbnail version will be downloaded locally. To filter images, click on the `settings` button to enable or disable the NSFW filter or include blacklist tags. Blacklist tags will prevent an image with that tag from being downloaded. For example, if images of cats with dogs show up in your `cats` query and you don't want dogs, put `dogs` into the blacklist. Hit `Submit` to get images. This will open the image review window.

Images can be rejected in the image review window by clicking on them. `Show common tags` will show a list of common tags that are also associated with the current selection of images. `Export Category` will export the images from the database into the local hard drive. Clicking on submit will put the current images into the db and reject those that have been selected.

The main window also allows the user to review images by tag by clicking on `Review Images`.

After other categories have been downloaded and reviewed, the images can be sent to the 'remote' server for training. There are options there to send the image urls over for the server to download the full sized versions of the images. The remote server can be reset to clear all the tables. There are options to check if the database has enough data to start training and to start training. If allowable, the remote server can be shut down if there are no other users connected. The remote server can be started by runnning `server.py`.

The local database can be reset by deleting the db file.

# Files
There are three important files in the project.

`client.py` launches the GUI and is the main entry point for the application.
`data.py` handles the database and downloading of images to the database.
`server.py` launches an instance of the remote server that the client can connect to for the hypothetical training.

`images.db` gets created when no such database exists. It stores the local thumbnail versions of the images and the metadata associated with each image.
`serverimages.db` gets created on the 'server' and stores the full size image files.

Miscellaneous test files were written to test the main files.

# Slides
The slides are available at https://docs.google.com/presentation/d/1VjEZNSGiX5WQ7owbERmVV7ALdXEMj2wZPv9BFNmggck/edit?usp=sharing
