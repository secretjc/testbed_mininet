cd ~/
ssh ms0714.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0721.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0712.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp

cat tmp.tmp | ssh ms0714.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0721.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0712.utah.cloudlab.us "cat >> .ssh/authorized_keys"
