#!/usr/bin/env python3
import pandas as pd
import markdown
from tqdm import tqdm
import numpy as np
import io
from PIL import Image
import weasyprint
from matplotlib import pyplot as plt
df_global = pd.read_csv("total_compiled.csv")
import folium
# ave_lat = 23.5
# ave_lon = 122.5

# # Load map centred on average coordinates

# #add a markers
# for each in points:
#     folium.Marker(list(each)).add_to(my_map)

# #add lines
# folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(my_map)

# Save map
# my_map.save("./out.html")

def get_details(latitude, longitude, eps=0.2):

    return df_global[
        ((df_global["latitude"] <= latitude + eps) & (df_global["latitude"] > latitude - eps))
        & ((df_global["longitude"] <= longitude + eps) & (df_global["longitude"] > longitude - eps))
    ]


def get_line_details(lat_1, lon_1, lat_2, lon_2, len_coeff=0.5):
    num=int(np.ceil(((lat_1-lat_2)**2+(lon_1-lon_2)**2)/len_coeff))
    points =  np.linspace((lat_1,lon_1),(lat_2,lon_2),num=num)
    details = []
    totals = 0
    highest_risk = (lat_1,lon_1)
    risk = -1
    for x in points:
        details.append(get_details(x[0],x[1]))
        totals+=len(details[-1])
    if totals>0:
        for i,x in enumerate(points):
            plt.scatter(x[1],x[0],c="r",alpha=0.7, s = 1000*len(details[i])/totals)
            if len(details[i])/totals > risk:
                risk = len(details[i])/totals
                highest_risk = (x[0],x[1])
            plt.scatter(x[1],x[0],c="g")
    return pd.concat(details),points, highest_risk,risk

def pd_to_text_details(df,points, high_risks, zoom=5):
    # p = np.array(points).flatten()
    # print(p.shape)
    # p = p.reshape(int(len(p)/2),2)
    p = points
    ave_lat, ave_lon = p.mean(axis=0)
    min_lat,min_lon = np.min(p,axis=0)
    max_lat,max_lon = np.max(p,axis=0)
    my_map = folium.Map(location=[ave_lat, ave_lon], min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon, max_bounds=True, zoom_start=zoom)
    # for each in points:
    #     folium.Marker(list(each)).add_to(my_map)
    #add lines
    folium.PolyLine(p, color="red", weight=2.5, opacity=1).add_to(my_map)

    my_map.save("./out.html")
    img_data = my_map._to_png()
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((640,326))
    img.save('image.png')

    print("Number of species affected: {}".format(len(df)))
    print("List of species affected: (Top 10)")

    list_species = df.species.unique()
    spec_meta = []
    for sp in list_species:
        spec_meta.append((sp,len(df[df["species"]==sp])))
    spec_meta.sort(key=lambda x: x[1], reverse=True)
    rist_str = [("- {} : {}".format(sp,cnt)) for sp,cnt in spec_meta[:min(10,len(spec_meta))]]
    # for idx, row in tqdm(df.iterrows()):
    #     plt.scatter(row.latitude,row.longitude,c="b")
    plt.ylim(min_lat-5, max_lat+5)
    plt.xlim(min_lon-5, max_lon+5)
    plt.savefig("image_2.png")
    plt.close()
    local_df = df_global[
        (df_global["latitude"] <= max_lat+20) & (df_global["latitude"] > min_lat-20) & (df_global["longitude"] <= max_lon+10) & (df_global["longitude"] > min_lon-10)
    ]
    # print(df)
    # print(local_df)
    local_df.plot.scatter("longitude","latitude", c="b", alpha = 0.5, s=0.8)
    plt.ylim(min_lat-20, max_lat+20)
    plt.xlim(min_lon-10, max_lon+10)
    plt.savefig("regional_dist.png")
    plt.close()


    print("Risk index: {}".format(np.log(len(df))))
    report = """# Assessment Report
### Route from {} to {}
![Map of route](./image.png "Route Map")
## Number of Species Affected: {}
### Top 10 species affected
{}
## Risk index {:.2f}
### Risk areas
![Map of route](./image_2.png "Route Map")
### Regional Species distribution
![Map of route](./regional_dist.png "Route Map")

## Higest risk regions
{}
""".format(points[0],points[-1],len(df),"\n".join(rist_str),float(np.log(len(df))), "- "+"\n- ".join(["({:.2f},{:.2f})".format(float(x[0]), float(x[1])) for x in high_risks]))
    plt.close()
    return report
    # plt.scatter(latitude,longitude,c="r", alpha=0.5)

def report_driver(list_of_ll, zoom = 5):
    points_list = []
    df_list = []
    high_risks = []
    for i in range(len(list_of_ll)-1):
        df,points,highest_risk,risk = get_line_details(list_of_ll[i][0], list_of_ll[i][1],list_of_ll[i+1][0],list_of_ll[i+1][1])
        points_list.append(points)
        high_risks.append(highest_risk)
        df_list.append(df)
    df_list = pd.concat(df_list)
    report = pd_to_text_details(df_list,np.concatenate(points_list), high_risks, zoom=zoom)
    # print(report)
    report_html = markdown.markdown(report)
    report_file = open("report.html","w")
    report_file.write(report_html)
    report_file.close()
    report_pdf = weasyprint.HTML("./report.html").write_pdf()
    report_file = open("report.pdf","wb")
    report_file.write(report_pdf)
    report_file.close()

    return report
