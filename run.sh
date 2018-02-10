if [ $# -eq 0 ]
then
    echo "No argument supplied"
    exit 1
fi

file=$1
ssh -t seb@192.168.0.30 \
"cd /home/seb/Development/CSE237A/final_project && \
scp seb@192.168.0.15:/home/seb/Development/college/year5/winter18/CSE237A/final_project/$file . && \
sudo python $file"

