   M S B A M L   `   `   `  ���� O  Kmscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e0891&clr-namespace:System;assembly=mscorlibSystem   RPS_ARCGIS_SCENARIO_MANAGER#   ManageScenariosWPF.MainWindow   R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     @basics-http://schemas.microsoft.com/wpf/2008/toolkit     6sys&clr-namespace:System;assembly=mscorlib     ` \ESRI.ArcGIS.Client.Local, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944b ^ESRI.ArcGIS.Client.Toolkit, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944n jESRI.ArcGIS.Client.Toolkit.DataSources, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944Z	 VESRI.ArcGIS.Client, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944;esri*http://schemas.esri.com/arcgis/client/2009    	 $��675.6��$
��1100��  � Title$)  #RPS OilMap Scenario Manager: Aramco��.��� 
�������$��0,10,-0.4,-20.4q� � 	Resources ��%     � ColumnDefinitions �� $	��276 ��� �� $��0 ��� $	��280 �.+�0  *ESRI.ArcGIS.Client.Toolkit.FeatureDataGrid  -     Name$ 
MyDataGrid��$��0��
���   � J� RenderTransformOrigin$ 0.5,0.5&�$��0,0,529.4,26q�$��2��z�V� .~��� ��  �� AngleY$ 0.273Q��� T�  T� Y$ 0.715Q� 	 ESRI.ArcGIS.Client.Map  -     Name$ MyMap��$��1��   IsLogoVisible .  	   
WrapAround	 . 
   UseAcceleratedDisplay
 . $��10,-15,7.6,158.4q�$	��492��$��Bottom=�   Layers. 3 	 -ESRI.ArcGIS.Client.ArcGISTiledMapServiceLayer   	 ESRI.ArcGIS.Client.Layer	   ID$ StreetMapLayer��
   Url$S Mhttp://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer���� -    ��Name$ ResponseTextBlock��$��1��$-��'Manage OilMap Scenarios:  Status Window�� �� TextAlignment$
 Left=� �� TextWrapping$
 Wrap=�
���   �$
��Left=�$ �� HorizontalScrollBarVisibility$
 Auto=�" �� VerticalScrollBarVisibility$
 Auto=�$	��273��$��536,10,0,10q�$��3��.��� $��2��$��0,0,364.4,0q�.+��� $��301,534,-321,87q�$Z��TExample: https://test.com/server/rest/services/oilmap/oilspill/FeatureServer|'token'��$��10(� � ToolTip$  ��$��Italic$�$
��Bold"��� -   $��urlText��$��301,503,-321,127q�$��enter feature service url��$��10(�$ enter feature service url���� -    ��Name$ RefreshScenarioButton��$��Refresh Scenarios��$% Request Scenarios from Service.��$��334,576,-21.2,47.6q� K� ZIndex$ 1��$ 1,0.5&�$
��Left=�$	��137���� -   $ DeleteScenarioButton��$��Delete Scenario(s)��$s mSelect scenario(s) in the data grid.  Click 'Delete Scenarios' to delete all data related to the scenario(s).��$��579,574,-266.2,46.6q�$ 1��$ 0.5,0.5&�$
��Left=�$	��137��