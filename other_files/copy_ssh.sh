cd ~/
ssh ms0344.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0329.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0313.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0338.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0310.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp
ssh ms0305.utah.cloudlab.us cat .ssh/id_rsa.pub >> tmp.tmp

cat tmp.tmp | ssh ms0344.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0329.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0313.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0338.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0310.utah.cloudlab.us "cat >> .ssh/authorized_keys"
cat tmp.tmp | ssh ms0305.utah.cloudlab.us "cat >> .ssh/authorized_keys"
