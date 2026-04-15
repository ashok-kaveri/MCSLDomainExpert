# Packing Methods in the Shopify Multi-Carrier Shipping Label App

**Source:** https://www.pluginhive.com/knowledge-base/packing-methods-shopify-multi-carrier-shipping-label-app/
**App:** Shopify Multi Carrier Shipping Label App (MCSL)
**Note:** Some screenshots may show older app UI — all text content is current.

---

# Packing Methods in the Shopify Multi-Carrier Shipping Label App

Packing your products in the right way is not only important for the seamless delivery of your package but also for saving shipping costs. Shopify has certain limitations in handling the packing process based on product dimensions. So, it is really important to have a solution that lets you handle the packaging process with ease and saves on shipping costs. One of the easiest solutions is to use the [**Shopify Multi Carrier Shipping Label app**](https://apps.shopify.com/multi-carrier-shipping-label) which helps you automate this process.

This guide explains the different packing methods in the Shopify Multi-Carrier Shipping Label app and how you can use these methods to automate your packaging process.

* * *

## On this page

  * **Weight based Packing: Based on the products’ weight**
  * **Box Packing: Based on the products’ weight & dimensions**
  * **Stack Packing: Based on the products’ height**
  * **Quantity based packing: Based on the products’ quantity**
  * **Enabling the volumetric weight of a product**

* * *

The Shopify Multi-Carrier Shipping Label app offers the most advanced packaging methods that are based on the product weight as well as dimensions. To configure the packing method, head to App Settings –> Shipping –> Packaging, and choose the required packing method. Below are the four parcel packing methods in Shopify Multi-Carrier Shipping Label App: 

1\. Weight-based Packing  
2\. Box Packing  
3\. Stack Packing  
4\. Quantity-based Packing

* * *

## Weight-based Packing: Based on the products’ weight 

This packing method is based on the products’ weight. You can set a **max. weight** (maximum weight) limit for your box and the app automatically packs the maximum number of products possible in this box based on the max. weight defined.

This is the recommended packing method since most often weight is used as a parameter to handle the packaging and calculate accurate shipping rates. So, by default, the app will calculate the rates based on this packaging method.

In the below image, the max. weight is configured as 50 lbs. This means that in this particular box, items with a maximum weight of 50 lbs can be packed. So, as soon as the weight of the entire package crosses this value (50 lbs), the app will automatically select another box, and the remaining items are packed.

* * *

* * *

Understanding the method with an example; you have eight items and each of them weighs 10 lbs. The max. weight of the box is 50 lbs. So, five of them go into one package and the next three will go into another package since the ‘Max Weight’ set here is 50 lbs.

Now, if the max weight is 50 lbs and the product weight is 60 lbs, the product cannot be packed in the box and no rates will be provided at checkout, and the label generation will fail. In this case, you have to add the max. weight as 60 lbs so that, the product is packed correctly into the box.

Under the advanced configuration, you have the option to configure the **box weight** and also add a **max. quantity** that will be packed in a box.

* * *

## Box Packing: Based on the products’ weight & dimensions

This is an advanced packing method that is entirely based on the **box Volume, Dimensions, and Weight**.

When your products have different weights and dimensions, this packing method allows you to set up different packages based on the products’ weight & dimensions. So, whenever a customer places an order, the app automatically chooses the right box and calculates the rates accordingly. 

Ensure that you have entered the product dimensions under the “Products” section to use the box packing method as shown below.

* * *

* * *

In this method, the volume of the products is used to fit the total volume of the packages that you add. A box is filled based on the dimensions of the product until the box is filled or a minimum volume is left vacant. If the next unpacked product has a volume greater than the vacant volume, it goes into the next box and this process is continued until all products are packed properly.

* * *

* * *

In this method, you can create boxes based on your product weight & dimensions. You can add the Inner and Outer dimensions of the box, the weight of the box, the max weight, and the buffer height, as shown below.

**Buffer height** : This allows you to give a percentile adjustment value while packing the products. For example, if you have set up the box height as 100 cm, and you have a product with 25 cm height, you can fit 4 items in the particular box. But, if the product height is slightly higher, (maybe 27.5 cm), you would not be able to fit the products properly. To handle this, you can add a 10% buffer height, which will increase the height, and 4 items can be correctly packed in the box.

* * *

## Stack Packing: Based on the products’ height

The Stack packing method is based on the product height. You can add a box based on your product dimensions and the app automatically packs the products one over the other, based on the height configured under this packing method. 

* * *

* * *

You can also add a **Buffer Height** similar to box packing if required. Also, this method allows you to add the **max.weight** of the box as well, which allows the app to pack the maximum number of products in the box based on this weight.

* * *

### How Stack Packing Ensures Efficient Packing

If you sell items individually and also offer bundled sets containing multiple items, you might use a variety of box sizes to accommodate all combinations. The Multi-Carrier Shipping Label app uses “Stack” Box Packing to offer a smarter solution.

For instance, consider a customer who orders a set containing two individual items. Both items have identical dimensions 5.5 x 5.5 x 12.2 in. Here’s how the app tackles this challenge:

  * The app analyzes the dimensions of both items and finds potential boxes that can accommodate the products.
  * It prioritizes stacking the products on top of each other to perfectly fit both items & minimize wasted space

The app employs a sophisticated algorithm to achieve optimal packing. It considers factors like:

  * Individual item dimensions compared to potential box sizes.
  * Total order volume compared to box volume capacity
  * Total order weight compared to the box’s maximum weight limit
  * Combining the height of the products if the “Stack” option is enabled to determine the best-fitting box

* * *

**_Important Note_**   
  
The app doesn’t account for product rotation within the box.   

* * *

If you’re looking to streamline your shipping process and save on costs, intelligent box packing offers a valuable solution. By considering this concept and potentially adjusting product or box dimensions, you can experience the benefits of efficient packing with the Multi-Carrier Shipping Label app.

**Want to learn more? Watch our Box Packing Video for a deeper dive into how this feature works.**

* * *

## Quantity-based packing: Based on the products’ quantity

Using the quantity-based packing method, you can set up the packing based on the number of items that can be packed in one box. Add a box based on your product dimensions and you can set the **max.** **quantity** that can be packed in one box.

* * *

* * *

For example, in the image above, the max. quantity is set as 10. This means that only 10 items will be packed in this box and a new box will be generated for the 11th item. 

Also, this packing method can be used if you would like to pack your items individually. To do this, you can set the max. quantity as 1, and provide the weight and dimensions the same as the product weight and dimensions. This means that only one item will be packed in each box.

* * *

## Enabling the volumetric weight of a product

To choose the weight of the product, the app checks if the volumetric weight is enabled or not during the **Box packing and Stack packing** process.

#### If the volumetric weight of the product is not enabled

If the volumetric weight is not enabled under the app, the **actual weight & dimensions of the product **will be chosen as the**product weight & dimensions** for the packing process.

#### If the volumetric weight of the product is enabled

If the volumetric weight is enabled, as shown above, the **volumetric weight of all the products is calculated.** **The actual weight of the product and the volumetric weight are compared and the highest among them is chosen** for the packing process.

For example, if the actual weight of a product is 5 lbs and the volumetric weight is 7 lbs, the volumetric weight of 7 lbs will be chosen as the product weight for the Box Packing and Stack packing process.

### Calculation of the Volumetric weight of a product

You can calculate and verify the dimensional weight of your products from different carrier websites as given below. 

  * **[FedEx volumetric weight calculation](https://shipnow.gb.fedex.com/volume-calculator)**
  * [**DHL volumetric weight calculation**](https://www.dhl.com/en/tools/volumetric_weight_express.html)
  * **[UPS volumetric weight calculation](https://www.ups.com/us/en/supplychain/freight/chargeable-and-volumetric-weight-calculator.page)**
  * [**USPS/Stamps volumetric weight calculation**](https://www.stamps.com/usps/dimensional-weight/)
  * [**Canada Post volumetric weight calculation**](https://www.canadapost.ca/cpo/mc/assets/pdf/business/custguide_amend8_en.pdf)
  * [**Parcelforce volumetric weight calculation**](https://www.parcelforce.com/sites/default/files/Calculating_Volumetric_Weight_Final_220310.pdf)

* * *

### Weight and Volume Based Packing

Weight and volume-based packing help when shipping things like cotton. Since cotton can be light but take up a lot of space, it’s important to consider both its weight and how much space it needs. If we don’t do this, the shipping rates cost might vary.

For example, imagine we’re sending a bunch of cotton shirts. If we only look at how heavy they are and not how much space they take up, the shipping cost may vary. It is the same if we take into account their volume and not weight.

By using weight and volume-based packing, we can make sure to take both weight and volume into account to get accurate shipping rates.

* * *

### Calculation of Weight and Volume-Based Packing

The first greatest value among the dimensions will be taken as **Length** (any value)  
The second greatest value among the dimensions will be taken as **Width**(any value)

To calculate the height, use the following formula:  
**Height = Volume of product – P1 (V1) + Volume of product – P2 (V2) / length*width**

Let’s say you have two Products P1 and P2 with dimensions as follows:

| Length| Width| Height| Volume  
---|---|---|---|---  
P1| 07| 04| 05| 140  
P2| 08| 05| 03| 120  
  
Length – 8 Width – 7  
To calculate height: 140 + 120 / 8*7 = 4.642

Therefore, the dimensions of the package will be as follows:  
Length – 8; Width – 7; Height – 4.642

If you have any queries with the setting up of the app, you can look into [**setting up the**](https://www.pluginhive.com/knowledge-base/setting-up-shopify-multi-carrier-shipping-label-app/)Shopify Multi-Carrier Shipping Label app. Also, for any issues with the app, the troubleshooting guide for the **Shopify Multi-Carrier Shipping Label app** would help you.

Also, if you have any other queries regarding the packaging process with the app, do [**contact PluginHive support**](https://www.pluginhive.com/support/).

[ Previous  How to configure carrier account in the Shopify Multi Carrier Shipping Label app?  ](https://www.pluginhive.com/knowledge-base/configure-carrier-account-in-shopify-multi-carrier-shipping-label-app/)

[ Next  Calculate shipping costs based on Shopify shipping zones  ](https://www.pluginhive.com/knowledge-base/shipping-costs-based-on-shopify-shipping-zones/)
