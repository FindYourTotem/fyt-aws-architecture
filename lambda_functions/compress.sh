cur_dir=$PWD

for folder in */ ; do
	cd $cur_dir/$folder
	zip -r ${folder%/}.zip ./*
	mv ${folder%/}.zip ../
done