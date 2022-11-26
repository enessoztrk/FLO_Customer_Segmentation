###############################################################
             # Customer Segmentation with RFM #
###############################################################

###############################################################
# TASK 1: Data Understanding
###############################################################
import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width',1000)


# 1. Read the data flo_data_20K.csv. Make a copy of the dataframe.
df_ = pd.read_csv("flo_data_20k.csv")
df = df_.copy()
df.head()


# 2. In the dataset
         # a. top 10 observations,
         # b. variable names,
         # c. dimension,
         # D. descriptive statistics,
         # e. null value,
         # f. variable types, review.
df.head(10)
df.columns
df.shape
df.describe().T
df.isnull().sum()
df.info()


# 3. Omnichannel means that customers shop from both online and offline platforms.
# Create new variables for the total number of purchases and spending of each customer.
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]


# 4. Examine the variable types. Change the type of variables that express date to date.
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()


# 5. Look at the distribution of the number of customers in the shopping channels, the total number of products purchased and total expenditures.
df.groupby("order_channel").agg({"master_id":"count", #.unıque
                                 "order_num_total":"sum",
                                 "customer_value_total":"sum"})


# 6. Rank the top 10 customers with the most revenue.
df.sort_values("customer_value_total", ascending=False)[:10]


# 7. Rank the top 10 customers with the most orders.
df.sort_values("order_num_total", ascending=False)[:10]


# 8. Functionalize the data provisioning process.
def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return df


###############################################################
# TASK 2: Calculating RFM Metrics
###############################################################
# Analysis date 2 days after the last shopping date in the data set
df["last_order_date"].max() # 2021-05-30
analysis_date = dt.datetime(2021,6,1)


# A new rfm dataframe with customer_id, recency, frequnecy and monetary values
rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]')
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()


###############################################################
# GÖREV 3: Calculating RF and RFM Scores
###############################################################
# Converting Recency, Frequency and Monetary metrics to scores between 1-5 with the help of qcut and
# Saving these scores as recency_score, frequency_score and monetary_score
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm.head()


# Express recency_score and frequency_score as a single variable and save it as RF_SCORE
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))


# 3. Expressing recency_score and frequency_score and monetary_score as a single variable and saving it as RFM_SCORE
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))

rfm.head()


###############################################################
# TASK 4: Defining RF Scores as Segments
###############################################################
# Segment definition and conversion of RF_SCORE to segments with the help of defined seg_map so that the generated RFM scores can be explained more clearly.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)
rfm.head()


###############################################################
# TASK 5: Time for action!
###############################################################
# 1. Examine the recency, frequency and monetary averages of the segments.
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])
#                          recency       frequency       monetary
#                        mean count      mean count     mean count
# segment
# about_to_sleep       113.79  1629      2.40  1629   359.01  1629
# at_Risk              241.61  3131      4.47  3131   646.61  3131
# cant_loose           235.44  1200     10.70  1200  1474.47  1200
# champions             17.11  1932      8.93  1932  1406.63  1932
# hibernating          247.95  3604      2.39  3604   366.27  3604
# loyal_customers       82.59  3361      8.37  3361  1216.82  3361
# need_attention       113.83   823      3.73   823   562.14   823
# new_customers         17.92   680      2.00   680   339.96   680
# potential_loyalists   37.16  2938      3.30  2938   533.18  2938
# promising             58.92   647      2.00   647   335.67   647


# 2. With the help of RFM analysis, find the customers in the relevant profile for 2 cases and save the customer IDs to the csv.
# a. FLO includes a new women's shoe brand. The product prices of the brand it includes are above the general customer preferences. Therefore, the brand
# It is desired to contact the customers in the profile that will be interested in # promotion and product sales. These customers are loyal and
# It was planned to have shoppers from the women category. Add the id numbers of the customers to the csv file with the new_brand_target_customer_id.cvs
# Save it as.
target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id.csv", index=False)
cust_ids.shape

rfm.head()
df.head()


# b. Up to 40% discount is planned for Men's and Children's products. Long time but good past customers interested in categories related to this discount
# non-shopping and new customers are specifically targeted. Enter the ids of the customers in the appropriate profile into the csv file discount_target_customer_ids.csv
# Save it as
target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)


###############################################################
# # Streamline the entire process.
###############################################################
def create_rfm(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)


    dataframe["last_order_date"].max()  # 2021-05-30
    analysis_date = dt.datetime(2021, 6, 1)
    rfm = pd.DataFrame()
    rfm["customer_id"] = dataframe["master_id"]
    rfm["recency"] = (analysis_date - dataframe["last_order_date"]).astype('timedelta64[D]')
    rfm["frequency"] = dataframe["order_num_total"]
    rfm["monetary"] = dataframe["customer_value_total"]

    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))


    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

    return rfm[["customer_id", "recency","frequency","monetary","RF_SCORE","RFM_SCORE","segment"]]

rfm_df = create_rfm(df)