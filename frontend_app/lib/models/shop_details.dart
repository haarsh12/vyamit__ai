import 'dart:typed_data';

class ShopDetails {
  String shopName;
  String ownerName;
  String address;
  String phone1;
  String phone2;
  Uint8List? qrCodeBytes; // Added for Printer Logic

  ShopDetails({
    required this.shopName,
    required this.ownerName,
    required this.address,
    required this.phone1,
    required this.phone2,
    this.qrCodeBytes,
  });
}
