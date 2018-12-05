# How do I get an existing simulation-trained submission to run on the physical Duckiebot?

This documentation is a bit of a brain dump and was not written for the next 10 generations to come. This is all a very temporary solution either for the eager or for the poor students who agreed to go through with this. I salute thee.

## 0 ) Prerequisites

- Duckiebot, 2018 model, RPi 3B+ with the new HAT.
- 5Ghz WiFi with internet connection and have the Duckiebot connected to that. If it's not clear how to do that, drop me an email/slack.
- A laptop/PC with docker installed.

## 1 ) Get the robot ready

Grab the Duckiebot. Stop all containers. Or don't. IDK. I wiped my Duckiebot clean meaning when it's booting, the only two containers that start by default are the `watchtower` and `portainer`. Probably this works if you don't stop existing containers, but no guarantees. If this is too much effort for somebody, contact me and I'll send them a disk image of my Ducky.

SSH in to the Duckie. Fetch the most recent `duckietown-slimremote` container. Currently that's `fgolemo/duckietown-slimremote:testing`:

    ssh YOUR_DUCKIE_HOSTNAME # in my case 'duckmylife3.local'
    
Find out the IP address of your Duckiebot **(and note this somewhere for later)**

    ip addr | grep 'wlan0' -A 1 | grep 'inet' | grep -oE "\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-4]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    
Launch the `slimremote` container    
    
    docker pull fgolemo/duckietown-slimremote:testing
    
And when this is done, just run the container:

    docker run -it -p 5558:5558 -p 8902:8902 --privileged \ 
    -e DUCKIETOWN_MAXSPEED=0.5 -v /dev/input:/dev/input \
     fgolemo/duckietown-slimremote:testing
    
Where `DUCKIETOWN_MAXSPEED` is ... the maximum speed at which the motors will go (in range `[0;1]`.

This will keep the slimremote running in your terminal. The robot is now ready for incomming connections. Open a new terminal/tab.

Just to be sure, this should output (among some other things):

    picamera running with 320x240 px at 15Hz
    Robot listening to incoming connections...

## 2 ) Prepare the submission

This is the "fun" part. The following is to be done on your laptop.

Grad a submission that you'd like to run on the Duckiebot. What you want is the Dockerhub address and version like `USERNAME/aido1_lf1_r3-v3-submission:VERSION`. For example, I went to the leaderboard at https://challenges.duckietown.org/v3/humans/challenges/aido1_LF1_r3-v3/leaderboard and clicked on the first 3 submissions. Let's say we take the leader (as of writing), heyt0ny: https://challenges.duckietown.org/v3/humans/submissions/1372. Scroll all the way down on the submission and find the line with `step1-simulation` in the table at the bottom. Click on `29 artifacts` to expand it and click on `3 KB	docker-compose.yaml`. In the new window, Find the value of `services/solution/image`. In the case of this example, that'd be `image: heyt0ny/aido1_lf1_r3-v3-submission:2018_11_26_16_43_48`. You need the last part of this, `heyt0ny/aido1_lf1_r3-v3-submission:2018_11_26_16_43_48`.

Pull the image:

    docker pull USERNAME/aido1_lf1_r3-v3-submission:VERSION 
    
    # so in my example case that would be
    # docker pull heyt0ny/aido1_lf1_r3-v3-submission:2018_11_26_16_43_48
    
    
Now we need to make some changes to this image, because it's not using the most recent version of the `duckietown-slimremote`. And  we need to make sure it has OpenCV installed.
There a few ways of doing this, but the one I found the easiest, is this:
Start the image, but leave out some important bit (don't mount the task description). This forces the image to start but not do anything for 10 minutes after which it shuts down.    

    docker run -d --net host --privileged -e username=root -e \
    challenge_step_name=step1-simulation -e uid=0 \
    -e challenge_name=aido1_LF1_r3-v3 -e DUCKIEBOT_NAME=DUCKIE_NAME \
    -e DUCKIEBOT_IP=DUCKIE_IP -e DUCKIETOWN_SERVER=DUCKIE_HOST \
    USERNAME/ aido1_lf1_r3-v3-submission:VERSION

where

    DUCKIE_NAME = name of your Duckiebot, without ".local" like "duckmylife3"
    DUCKIE_IP   = IP of the Duckiebot, as noted earlier, like "192.168.0.188"
    DUCKIE_HOST = name of Duckiebot plus ".local", like "duckmylife3.local"
    USERNAME    = name of the submission you wanna modify, like "heyt0ny"
    VERSION     = date of the submission, like "2018_11_26_16_43_48"
    
So in my example this line becomes:

    docker run -d --net host --privileged -e username=root -e \
    challenge_step_name=step1-simulation -e uid=0 \
    -e challenge_name=aido1_LF1_r3-v3 -e DUCKIEBOT_NAME=duckmylife3 \
    -e DUCKIEBOT_IP=10.42.0.238 -e DUCKIETOWN_SERVER=duckmylife3.local \
    heyt0ny/aido1_lf1_r3-v3-submission:2018_11_26_16_43_48
    
...
Now that this is running in the background, find out the container name:

    docker ps
    
And look on the far right side for something silly like `naughty_payne`

Now connect a shell to that container:
    
    docker exec -it DOCKERNAME /bin/bash
    
    # where DOCKERNAME = the name you got from "docker ps" 
    # like in my case,
    
    # docker exec -it naughty_payne /bin/bash
    
Now comes the tricky part. In 9 out of 10 cases the `duckietown-slimremote` repo sits at `/workspace/src/duckietown-slimremote`. Verify this now. If there is no repo here, find its location by issueing the command:

    find / -name "13-test*" # that's the name of a random script from that repo
    
Let's say the repo is indeed at that location, then you can `cd` into that directory and clone the new version of the repo:

    cd /workspace/src/duckietown-slimremote/ && \
    git config --global user.email "you@example.com" && \
    git config --global user.name "Your Name" && \
    git pull origin testing; \
    git reset --hard origin/testing
    
This should complete with something like `"HEAD is now at ..."`

**\<Bonus>** Verify that OpenCV is installed: this is true, again, 9/10 cases, but just so you know. Run python

    python
    
and see if you can import OpenCV

    import cv2
    
If this creates an error, install it via:

    conda install opencv # and press "y" when it asks you to
    
**\</Bonus>**

That's it, quit the shell

    exit
    
And now the **important** part: save the changes

    docker commit DOCKERNAME RANDOMNAME
    
    # where 
    # DOCKERNAME = the thing you found out via "docker ps", the name of this container
    # RANDOMNAME = some string that you can freely chose, like "ladida"
    
    # so in my example this would be
    # docker commit naughty_payne ladida
    
Halt the old container:

    docker container stop DOCKERNAME
    
    # e.g. docker container stop naughty_payne
    
And that's it for the preparation. Wasn't super hard, right? If you do this 2-3 times, you get into the rhythm. I mean you shouldn't because we're currently working on a solution for doing all this automatically, but you know... just in case.

## 3 ) Run the modified image on the robot

Create a folder somewhere, and name it `challenge-description`. 

    mkdir ~/challenge-description

Inside this folder, create a new test file called `description.yaml`. 

    touch ~/challenge-description/description.yaml

This is the task description for the container. Add the following line to this text file: `env: Duckietown-Lf-Lfv-Navv-Silent-v1` and save the text file.

    echo "env: Duckietown-Lf-Lfv-Navv-Silent-v1" > ~/challenge-description/description.yaml

Now you need to mount this into the modified container like so:

    docker run -it --net host --privileged -e username=root \
    -e challenge_step_name=step1-simulation -e uid=0 \
    -e challenge_name=aido1_LF1_r3-v3 -e DUCKIEBOT_NAME=DUCKIE_NAME \
    -e DUCKIEBOT_IP=DUCKIE_IP -e DUCKIETOWN_SERVER=DUCKIE_HOST \
    -v ~/challenge-description:/challenge-description RANDOMNAME
    
where

    DUCKIE_NAME = name of your Duckiebot, without ".local" like "duckmylife3"
    DUCKIE_IP   = IP of the Duckiebot, as noted earlier, like "192.168.0.188"
    DUCKIE_HOST = name of Duckiebot plus ".local", like "duckmylife3.local"
    RANDOMNAME  = name you came up with for the modified container

So in my example this becomes: 
    
    docker run -it --net host --privileged -e username=root \
    -e challenge_step_name=step1-simulation -e uid=0 \
    -e challenge_name=aido1_LF1_r3-v3 -e DUCKIEBOT_NAME=duckmylife3 \
    -e DUCKIEBOT_IP=10.42.0.238 -e DUCKIETOWN_SERVER=duckmylife3.local \
    -v ~/challenge-description:/challenge-description ladida
 
---

And voila. This should run the submission on your laptop with images streaming over WiFi.

If anything doesn't work, mail/slack me.

    
    
    