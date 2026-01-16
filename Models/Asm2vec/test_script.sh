docker run --rm -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
								-v $(pwd)/a2v_preprocessing_Dataset-3-training:/training_data \
								-v $(pwd):/output -it asm2vec /code/i2v_preprocessing.py \
								-d -w32 -a2v -i /input -v /training_data/vocabulary.csv -o /output/a2v_preprocessing_Dataset-Muaz-testing

docker run --rm -v $(pwd)/a2v_preprocessing_Dataset-Muaz-testing:/input \
								-v $(pwd)/asm2vec_checkpoint:/checkpoint \
								-v $(pwd):/output -it asm2vec /code/i2v.py \
								-d --asm2vec --inference -e10 -w32 --inputdir /input/ -c /checkpoint -o /output/asm2vec_inference_Dataset-Muaz-testing

echo -e "\n *** Results saved in $(pwd)/asm2vec_inference_Dataset-Muaz-testing/embeddings.csv\n"
echo "Converting results..."
python3 convert_asm2vec_results.py

mkdir -p ../../Results/csv
cp asm2vec_inference_Dataset-Muaz-testing/pairs_results_Dataset-Muaz_a2v.csv ../..//Results/csv/pairs_results_Dataset-Muaz_a2v.csv
echo -e "\n*** Pairs results saved in ../../Results/csv"
