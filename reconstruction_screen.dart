import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ReconstructionScreen extends StatefulWidget {
  const ReconstructionScreen({super.key});

  @override
  State<ReconstructionScreen> createState() => _ReconstructionScreenState();
}

class _ReconstructionScreenState extends State<ReconstructionScreen> {
  static const String _defaultPrompt =
      'ancient stone carving, megalithic heritage, Goa, detailed texture';

  final List<Offset?> _maskPoints = [];
  final GlobalKey _maskKey = GlobalKey();
  late final TextEditingController _promptController;

  Uint8List? _selectedImageBytes;
  Uint8List? _resultImage;
  bool _isLoading = false;
  bool _isLoadingUrl = true;
  String? _reconstructUrl;

  @override
  void initState() {
    super.initState();
    _promptController = TextEditingController(text: _defaultPrompt);
    _fetchReconstructUrl();
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  Future<void> _fetchReconstructUrl() async {
    try {
      final response = await Supabase.instance.client
          .from('config')
          .select('value')
          .eq('key', 'reconstruct_url')
          .single();

      final value = response['value']?.toString().trim();
      if (value == null || value.isEmpty) {
        throw Exception('config.reconstruct_url is empty');
      }

      if (!mounted) return;
      setState(() {
        _reconstructUrl = value;
        _isLoadingUrl = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _isLoadingUrl = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load reconstruction URL: $error')),
      );
    }
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;

    final bytes = await picked.readAsBytes();
    if (!mounted) return;

    setState(() {
      _selectedImageBytes = bytes;
      _maskPoints.clear();
      _resultImage = null;
    });
  }

  Future<Uint8List?> _captureMask() async {
    try {
      final boundary =
          _maskKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return null;

      final image = await boundary.toImage(pixelRatio: 1.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      return byteData?.buffer.asUint8List();
    } catch (error) {
      debugPrint('Mask capture error: $error');
      return null;
    }
  }

  Future<void> _reconstruct() async {
    if (_selectedImageBytes == null) {
      _showSnackBar('Please select an image first');
      return;
    }

    if (_reconstructUrl == null) {
      _showSnackBar('Server URL is not loaded yet. Try again.');
      return;
    }

    setState(() {
      _isLoading = true;
      _resultImage = null;
    });

    try {
      final maskBytes = await _captureMask();
      if (maskBytes == null) {
        throw Exception('Failed to capture mask');
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_reconstructUrl!),
      );
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          _selectedImageBytes!,
          filename: 'image.jpg',
        ),
      );
      request.files.add(
        http.MultipartFile.fromBytes('mask', maskBytes, filename: 'mask.png'),
      );
      request.fields['prompt'] = _promptController.text.trim().isEmpty
          ? _defaultPrompt
          : _promptController.text.trim();

      final response = await request.send().timeout(
        const Duration(seconds: 120),
      );

      if (response.statusCode != 200) {
        final body = await response.stream.bytesToString();
        throw Exception(
          body.isEmpty ? 'Server error: ${response.statusCode}' : body,
        );
      }

      final bytes = await response.stream.toBytes();
      if (!mounted) return;
      setState(() => _resultImage = bytes);
    } catch (error) {
      _showSnackBar('Error: $error');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _clearMask() {
    setState(() {
      _maskPoints.clear();
      _resultImage = null;
    });
  }

  void _showSnackBar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('The Time Machine'),
        backgroundColor: Colors.grey.shade900,
        foregroundColor: Colors.white,
        actions: [
          if (_selectedImageBytes != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Clear mask',
              onPressed: _clearMask,
            ),
        ],
      ),
      body: _isLoadingUrl
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const _StepLabel(step: '1', label: 'Select a heritage image'),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _pickImage,
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Choose from Gallery'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey.shade900,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                  if (_selectedImageBytes != null) ...[
                    const SizedBox(height: 24),
                    const _StepLabel(
                      step: '2',
                      label: 'Draw over the damaged area',
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: SizedBox(
                        height: 300,
                        child: Stack(
                          fit: StackFit.expand,
                          children: [
                            Image.memory(
                              _selectedImageBytes!,
                              fit: BoxFit.cover,
                            ),
                            RepaintBoundary(
                              key: _maskKey,
                              child: GestureDetector(
                                behavior: HitTestBehavior.opaque,
                                onPanUpdate: (details) {
                                  setState(() {
                                    _maskPoints.add(details.localPosition);
                                  });
                                },
                                onPanEnd: (_) {
                                  setState(() => _maskPoints.add(null));
                                },
                                child: CustomPaint(
                                  painter: _MaskPainter(_maskPoints),
                                  child: const SizedBox.expand(),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Paint with your finger over the area to reconstruct',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    const _StepLabel(
                      step: '3',
                      label: 'Describe what to reconstruct',
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _promptController,
                      minLines: 1,
                      maxLines: 3,
                      decoration: InputDecoration(
                        hintText:
                            'e.g. ancient laterite stone, Goan heritage...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 10,
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _reconstruct,
                      icon: _isLoading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.auto_fix_high),
                      label: Text(
                        _isLoading ? 'Reconstructing...' : 'Reconstruct',
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blueAccent,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                  if (_resultImage != null) ...[
                    const SizedBox(height: 24),
                    const _StepLabel(step: '4', label: 'Reconstruction result'),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Image.memory(
                        _resultImage!,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ],
                  const SizedBox(height: 40),
                ],
              ),
            ),
    );
  }
}

class _MaskPainter extends CustomPainter {
  final List<Offset?> points;

  _MaskPainter(this.points);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withAlpha(180)
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 30.0
      ..style = PaintingStyle.stroke;

    for (var index = 0; index < points.length - 1; index++) {
      final start = points[index];
      final end = points[index + 1];
      if (start != null && end != null) {
        canvas.drawLine(start, end, paint);
      }
    }
  }

  @override
  bool shouldRepaint(_MaskPainter oldDelegate) => true;
}

class _StepLabel extends StatelessWidget {
  final String step;
  final String label;

  const _StepLabel({required this.step, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: Colors.grey.shade900,
          child: Text(
            step,
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
          ),
        ),
      ],
    );
  }
}
