docker run --rm --name zeek_preprocessing -v $(pwd)/../../DBs/Dataset-adv/features/training/acfg_disasm_Dataset-adv_training:/input -v  $(pwd)/Preprocessing/zeek_intermediate/Dataset-Muaz-adv_training:/output -it zeek /code/zeek.py process /input /output --workers-num 28

docker run --rm --name zeek_preprocessing -v $(pwd)/../../DBs/Dataset-adv/features/validation/acfg_disasm_Dataset-adv_validation:/input -v  $(pwd)/Preprocessing/zeek_intermediate/Dataset-Muaz-adv_validation:/output -it zeek /code/zeek.py process /input /output --workers-num 28

docker run --rm -v $(pwd)/../../DBs:/input -v $(pwd)/NeuralNetwork:/output -it zeekneuralnetwork /code/zeek_nn.py --train --num_epochs 10 -c /code/model_checkpoint_blablablaseetestscript --dataset adv -o /output/Dataset-adv_training
