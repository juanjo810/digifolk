from app.api.routes.games import melodyGame
import sys

import evaluation.cleaning as cleaning
import evaluation.model_eval as model
import evaluation.thresh_eval as thresh
import evaluation.pattern_generation as pattern
import evaluation.similarity as similarity
import evaluation.melodyGame as melodyGame

if __name__ == "__main__":
    if sys.argv[1] == 'phrases_xml':
        cleaning.phrases_for_xml()
    elif sys.argv[1] == 'search':
        cleaning.search_note(sys.argv[2])
    elif sys.argv[1] == 'clean':
        cleaning.remove_staff_2()
    elif sys.argv[1] == 'midis':
        cleaning.create_midis()
    elif sys.argv[1] == 'oracle':
        thresh.create_test_oracle()
    elif sys.argv[1] == 'plot_comparison':
        thresh.oracle_comparison(sys.argv[2])
    elif sys.argv[1] == 'generation':
        model.generate_phrases(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == 'lerch':
        model.Lerch_Work_Flow()
    elif sys.argv[1] == 'abcs':
        cleaning.join_abcs_one_file()
    elif sys.argv[1] == 'show_abcs':
        cleaning.open_abc_database_as_mxl()
    elif sys.argv[1] == 'MEI':
        cleaning.open_mei()
    elif sys.argv[1] == 'pattern':
        pattern.generate_phrases(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == 'game':
        melodyGame.test_mel()
    elif sys.argv[1] == 'similarity':
        similarity.test_similarity_metric()
    elif sys.argv[1] == 'similarity_matrix':
        similarity.test_similarity_all()
