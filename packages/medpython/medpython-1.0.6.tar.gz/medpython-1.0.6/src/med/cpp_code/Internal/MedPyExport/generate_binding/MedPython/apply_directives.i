%rename(SerializableObject) MPSerializableObject;
%rename(SigVectorAdaptor) MPSigVectorAdaptor;
%rename(Sig) MPSig;
%rename(SigExporter) MPSigExporter;
%rename(PidRepository) MPPidRepository;
%rename(MedConvert) MPMedConvert;
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* pids_to_take, unsigned long long num_pids_to_take), (int* pids_to_take, unsigned long long num_pids_to_take), (int* pids_to_take, unsigned long long num_pids_to_take)}
%extend MPPidRepository{

void get_sig(const char * sig_name_str, bool translate=true, std::vector<int> * pids=nullptr, bool float32to64=true, bool free_signal=true, const char * regex_str=nullptr, const char * regex_filter=nullptr) {}
%pythoncode %{
      pids = property(MEDPY_GET_pids,None)
  %}
};
%extend MPSigVectorAdaptor{

%pythoncode %{
      type = property(MEDPY_GET_type,None)
      n_time_channels = property(MEDPY_GET_n_time_channels,None)
      n_val_channels = property(MEDPY_GET_n_val_channels,None)
      time_unit = property(MEDPY_GET_time_unit,None)
      size = property(MEDPY_GET_size,None)
  %}
};
%rename(PandasAdaptor) MPPandasAdaptor;
%apply (void** ARGOUTMVAR_ARRAY1, unsigned long long* DIM1, int* NPYDTC1) {(void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype), (void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype), (void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype)}
%rename(FeatureAttr) MPFeatureAttr;
%rename(StringFeatureAttrMapAdaptor) MPStringFeatureAttrMapAdaptor;
%rename(Features) MPFeatures;
%apply (float** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(float** float_out_buf, unsigned long long* float_out_buf_len)}
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* int_in_buf, unsigned long long int_in_buf_len)}
%extend MPFeatureAttr{

%pythoncode %{
      normalized = property(MEDPY_GET_normalized,MEDPY_SET_normalized)
      imputed = property(MEDPY_GET_imputed,MEDPY_SET_imputed)
      denorm_mean = property(MEDPY_GET_denorm_mean,MEDPY_SET_denorm_mean)
      denorm_sdv = property(MEDPY_GET_denorm_sdv,MEDPY_SET_denorm_sdv)
  %}
};
%extend MPFeatures{

%pythoncode %{
      data = property(MEDPY_GET_data,None)
      weights = property(MEDPY_GET_weights,None)
      samples = property(MEDPY_GET_samples,None)
      pid_pos_len = property(MEDPY_GET_pid_pos_len,None)
      attributes = property(MEDPY_GET_attributes,None)
      tags = property(MEDPY_GET_tags,None)
      time_unit = property(MEDPY_GET_time_unit,MEDPY_SET_time_unit)
      global_serial_id_cnt = property(MEDPY_GET_global_serial_id_cnt,MEDPY_SET_global_serial_id_cnt)
  %}
};
%rename(Mat) MPMat;
%apply (int** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(int** out_row_ids_buf, unsigned long long* out_row_ids_buf_len), (int** avg_buf, unsigned long long* avg_buf_len), (int** std_buf, unsigned long long* std_buf_len)}
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* row_ids_buf, unsigned long long row_ids_buf_len)}
%apply (float* IN_ARRAY1, unsigned long long DIM1) {(float* m_add, unsigned long long nrows_to_add), (float* m_add, unsigned long long ncols_to_add), (float* wgts, unsigned long long wgts_n), (float* external_avg, unsigned long long external_avg_n), (float* external_std, unsigned long long external_std_n)}
%apply (float** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(float** rowv, unsigned long long* rowv_n), (float** colv, unsigned long long* colv_n), (float** buf_avg, unsigned long long* buf_avg_n), (float** buf_std, unsigned long long* buf_std_n)}
%extend MPMat{

%pythoncode %{
      Normalize_Cols = property(MEDPY_GET_Normalize_Cols,None)
      Normalize_Rows = property(MEDPY_GET_Normalize_Rows,None)
      nrows = property(MEDPY_GET_nrows,None)
      ncols = property(MEDPY_GET_ncols,None)
      row_ids = property(MEDPY_GET_row_ids,MEDPY_SET_row_ids)
      signals = property(MEDPY_GET_signals,None)
      avg = property(MEDPY_GET_avg,None)
      std = property(MEDPY_GET_std,None)
      normalized_flag = property(MEDPY_GET_normalized_flag,MEDPY_SET_normalized_flag)
      transposed_flag = property(MEDPY_GET_transposed_flag,MEDPY_SET_transposed_flag)
      missing_value = property(MEDPY_GET_missing_value,MEDPY_SET_missing_value)
  %}
};
%rename(Dictionary) MPDictionary;
%apply (char** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(char** lut_array, unsigned long long* lut_size)}
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* members_array, unsigned long long members_size)}
%rename(Sample) MPSample;
%rename(SampleVectorAdaptor) MPSampleVectorAdaptor;
%rename(IdSamples) MPIdSamples;
%rename(IdSamplesVectorAdaptor) MPIdSamplesVectorAdaptor;
%rename(Samples) MPSamples;
%apply (float** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(float** out_predbuf, unsigned long long* out_predbuf_len), (float** preds_buf, unsigned long long* preds_buf_len), (float** y_buf, unsigned long long* y_buf_len), (float** categs_buf, unsigned long long* categs_buf_len)}
%apply (float* IN_ARRAY1, unsigned long long DIM1) {(float* in_predbuf, unsigned long long in_predbuf_len)}
%apply (int** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(int** ids, unsigned long long* num_ids)}
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int * patients, unsigned long long patient_size)}
%extend MPSample{

%pythoncode %{
      id = property(MEDPY_GET_id,MEDPY_SET_id)
      split = property(MEDPY_GET_split,MEDPY_SET_split)
      time = property(MEDPY_GET_time,MEDPY_SET_time)
      outcome = property(MEDPY_GET_outcome,MEDPY_SET_outcome)
      outcomeTime = property(MEDPY_GET_outcomeTime,MEDPY_SET_outcomeTime)
      prediction = property(MEDPY_GET_prediction,MEDPY_SET_prediction)
  %}
};
%extend MPIdSamples{

%pythoncode %{
      id = property(MEDPY_GET_id,MEDPY_SET_id)
      split = property(MEDPY_GET_split,MEDPY_SET_split)
      samples = property(MEDPY_GET_samples,None)
  %}
};
%extend MPSamples{

%pythoncode %{
      time_unit = property(MEDPY_GET_time_unit,MEDPY_SET_time_unit)
      idSamples = property(MEDPY_GET_idSamples,None)
  %}
};
%rename(RNG) MPRNG;
%rename(GlobalClass) MPGlobalClass;
%rename(CommonLib) MPCommonLib;
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* folds, unsigned long long num_folds)}
%extend MPGlobalClass{

%pythoncode %{
      default_time_unit = property(MEDPY_GET_default_time_unit,MEDPY_SET_default_time_unit)
      default_windows_time_unit = property(MEDPY_GET_default_windows_time_unit,MEDPY_SET_default_windows_time_unit)
  %}
};
%rename(Time) MPTime;
%rename(StringBtResultMap) MPStringBtResultMap;
%rename(Bootstrap) MPBootstrap;
%extend MPBootstrap{

%pythoncode %{
      sample_per_pid = property(MEDPY_GET_sample_per_pid,MEDPY_SET_sample_per_pid)
      nbootstrap = property(MEDPY_GET_nbootstrap,MEDPY_SET_nbootstrap)
      ROC_score_min_samples = property(MEDPY_GET_ROC_score_min_samples,MEDPY_SET_ROC_score_min_samples)
      ROC_score_bins = property(MEDPY_GET_ROC_score_bins,MEDPY_SET_ROC_score_bins)
      ROC_max_diff_working_point = property(MEDPY_GET_ROC_max_diff_working_point,MEDPY_SET_ROC_max_diff_working_point)
      ROC_score_resolution = property(MEDPY_GET_ROC_score_resolution,MEDPY_SET_ROC_score_resolution)
      ROC_use_score_working_points = property(MEDPY_GET_ROC_use_score_working_points,MEDPY_SET_ROC_use_score_working_points)
      ROC_working_point_FPR = property(MEDPY_GET_ROC_working_point_FPR,MEDPY_SET_ROC_working_point_FPR)
      ROC_working_point_PR = property(MEDPY_GET_ROC_working_point_PR,MEDPY_SET_ROC_working_point_PR)
      ROC_working_point_SENS = property(MEDPY_GET_ROC_working_point_SENS,MEDPY_SET_ROC_working_point_SENS)
      ROC_working_point_Score = property(MEDPY_GET_ROC_working_point_Score,MEDPY_SET_ROC_working_point_Score)
      ROC_working_point_TOPN = property(MEDPY_GET_ROC_working_point_TOPN,MEDPY_SET_ROC_working_point_TOPN)
  %}
};
%rename(Logger) MPLogger;
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* pids_to_take, unsigned long long num_pids_to_take)}
%apply (void** ARGOUTMVAR_ARRAY1, unsigned long long* DIM1, int* NPYDTC1) {(void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype), (void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype), (void** outarr1, unsigned long long* outarr1_sz, int* outarr1_npytype)}
%rename(PredictorTypes) MPPredictorTypes;
%rename(Predictor) MPPredictor;
%extend MPPredictor{

%pythoncode %{
      transpose_for_learn = property(MEDPY_GET_transpose_for_learn,MEDPY_SET_transpose_for_learn)
      normalize_for_learn = property(MEDPY_GET_normalize_for_learn,MEDPY_SET_normalize_for_learn)
      normalize_y_for_learn = property(MEDPY_GET_normalize_y_for_learn,MEDPY_SET_normalize_y_for_learn)
      transpose_for_predict = property(MEDPY_GET_transpose_for_predict,MEDPY_SET_transpose_for_predict)
      normalize_for_predict = property(MEDPY_GET_normalize_for_predict,MEDPY_SET_normalize_for_predict)
      model_features = property(MEDPY_GET_model_features,MEDPY_SET_model_features)
      features_count = property(MEDPY_GET_features_count,MEDPY_SET_features_count)
  %}
};
%rename(SampleFilter) MPSampleFilter;
%rename(Split) MPSplit;
%extend MPSplit{

%pythoncode %{
      nsplits = property(MEDPY_GET_nsplits,None)
      pid2split = property(MEDPY_GET_pid2split,None)
  %}
};
%rename(ModelStage) MPModelStage;
%rename(Model) MPModel;
%extend MPModel{

%pythoncode %{
      features = property(MEDPY_GET_features,None)
      verbosity = property(MEDPY_GET_verbosity,MEDPY_SET_verbosity)
  %}
};
%rename(IntIntMapAdaptor) MPIntIntMapAdaptor;
%rename(StringStringMapAdaptor) MPStringStringMapAdaptor;
%rename(StringFloatMapAdaptor) MPStringFloatMapAdaptor;
%rename(StringVecFloatMapAdaptor) MPStringVecFloatMapAdaptor;
%rename(IntPairIntIntMapAdaptor) MPIntPairIntIntMapAdaptor;
%rename(StringUOSetStringMapAdaptor) MPStringUOSetStringMapAdaptor;
%rename(IntStringMapAdaptor) MPIntStringMapAdaptor;
%rename(IntVecIntMapAdaptor) MPIntVecIntMapAdaptor;
%apply (int** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(int** intkeys_out_buf, unsigned long long* intkeys_out_buf_len), (int** int_out_buf, unsigned long long* int_out_buf_len), (int** intkeys_out_buf, unsigned long long* intkeys_out_buf_len), (int** int_out_buf, unsigned long long* int_out_buf_len)}
%apply (float** ARGOUTVIEWM_ARRAY1, unsigned long long* DIM1) {(float** float_out_buf, unsigned long long* float_out_buf_len)}
%apply (float* IN_ARRAY1, unsigned long long DIM1) {(float* float_in_buf, unsigned long long float_in_buf_len)}
%apply (int* IN_ARRAY1, unsigned long long DIM1) {(int* int_in_buf, unsigned long long int_in_buf_len), (int* int_in_buf, unsigned long long int_in_buf_len)}
