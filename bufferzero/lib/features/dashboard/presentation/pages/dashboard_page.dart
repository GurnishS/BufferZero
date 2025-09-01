import 'package:bufferzero/core/common/cubit/app_user_cubit.dart';
import 'package:bufferzero/core/common/widgets/bottom_nav_bar.dart';
import 'package:bufferzero/core/common/widgets/floating_download_button.dart';
import 'package:bufferzero/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

// Simple local model for dashboard videos. Kept private to this file.
class _Video {
  final String id;
  final String title;
  final String uploader;
  final String duration;
  final String thumbnail;
  _Video(this.id, this.title, this.uploader, this.duration, this.thumbnail);
}

class DashboardPage extends StatefulWidget {
  final AppUserCubit appUserCubit;

  const DashboardPage({super.key, required this.appUserCubit});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  // Controllers for each extractor horizontal list
  final Map<String, ScrollController> _controllers = {};

  // Sample extractor map is created once in state so controllers can be
  // initialized reliably.
  late final Map<String, List<_Video>> extractorMap;

  @override
  void initState() {
    super.initState();
    extractorMap = {
      'YouTube': List.generate(
        8,
        (i) => _Video(
          'yt_$i',
          'Why India\'s Censor Board is a Joke - part ${i + 1}',
          'Mohak Mangal',
          i % 3 == 0 ? '18:47' : (i % 3 == 1 ? '12:05' : '4:32'),
          'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
        ),
      ),
      'Hotstar': List.generate(
        6,
        (i) => _Video(
          'hs_$i',
          'Hotstar clip #${i + 1}',
          'Hotstar',
          '${2 + i}:12',
          '',
        ),
      ),
      'Dailymotion': List.generate(
        5,
        (i) => _Video(
          'dm_$i',
          'Dailymotion video ${i + 1}',
          'DM Uploader',
          '${3 + i}:45',
          '',
        ),
      ),
    };

    for (final key in extractorMap.keys) {
      _controllers[key] = ScrollController();
    }
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Sample video model used only by this page as placeholder data

    final Map<String, List<_Video>> extractorMap = {
      'YouTube': List.generate(
        8,
        (i) => _Video(
          'yt_$i',
          'Why India\'s Censor Board is a Joke - part ${i + 1}',
          'Mohak Mangal',
          i % 3 == 0 ? '18:47' : (i % 3 == 1 ? '12:05' : '4:32'),
          'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
        ),
      ),
      'Hotstar': List.generate(
        6,
        (i) => _Video(
          'hs_$i',
          'Hotstar clip #${i + 1}',
          'Hotstar',
          '${2 + i}:12',
          '',
        ),
      ),
      'Dailymotion': List.generate(
        5,
        (i) => _Video(
          'dm_$i',
          'Dailymotion video ${i + 1}',
          'DM Uploader',
          '${3 + i}:45',
          '',
        ),
      ),
    };

    Widget buildVideoCard(
      BuildContext ctx,
      _Video v,
      double width,
      ColorScheme cs,
      TextTheme tt,
    ) {
      return InkWell(
        onTap: () => ScaffoldMessenger.of(
          ctx,
        ).showSnackBar(SnackBar(content: Text('Open ${v.title}'))),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: width,
          margin: const EdgeInsets.only(right: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Thumbnail with duration overlay
              AspectRatio(
                aspectRatio: 16 / 9,
                child: Stack(
                  children: [
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.black12,
                        borderRadius: BorderRadius.circular(8),
                        image: v.thumbnail.isNotEmpty
                            ? DecorationImage(
                                image: NetworkImage(v.thumbnail),
                                fit: BoxFit.cover,
                              )
                            : null,
                      ),
                      child: v.thumbnail.isEmpty
                          ? Center(
                              child: Icon(
                                Icons.play_circle_fill,
                                size: 48,
                                color: cs.onSurface.withOpacity(0.6),
                              ),
                            )
                          : null,
                    ),
                    Positioned(
                      right: 8,
                      bottom: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.6),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          v.duration,
                          style: tt.bodySmall?.copyWith(color: Colors.white),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                v.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: tt.titleMedium,
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      v.uploader,
                      style: tt.bodySmall?.copyWith(
                        color: cs.onSurface.withOpacity(0.8),
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: cs.primaryContainer,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'Extractor',
                      style: tt.bodySmall?.copyWith(
                        color: cs.onPrimaryContainer,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      bottomNavigationBar: BottomNavBar(selectedIndex: 0),
      floatingActionButton: FloatingDownloadButton(),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final cs = Theme.of(context).colorScheme;
            final tt = Theme.of(context).textTheme;
            final width = constraints.maxWidth;
            // item width adapts to available width
            double itemWidth = 260;
            if (width < 600) itemWidth = 220;
            if (width >= 900) itemWidth = 300;

            return CustomScrollView(
              slivers: [
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                    child: Row(
                      children: [
                        Text('Discover', style: tt.headlineSmall),
                        const Spacer(),
                        ElevatedButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.search),
                          label: const Text('Explore'),
                          style: ElevatedButton.styleFrom(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // For each extractor show a section with horizontal scroller
                for (final entry in extractorMap.entries)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            child: Row(
                              children: [
                                Text(entry.key, style: tt.titleLarge),
                                const Spacer(),
                                TextButton(
                                  onPressed: () {},
                                  child: const Text('See all'),
                                ),
                              ],
                            ),
                          ),
                          SizedBox(
                            height: itemWidth * 9 / 16 + 110,
                            child: Stack(
                              children: [
                                Positioned.fill(
                                  child: Padding(
                                    padding: const EdgeInsets.only(
                                      left: 16,
                                      right: 8,
                                    ),
                                    child: ListView.builder(
                                      controller: _controllers[entry.key],
                                      scrollDirection: Axis.horizontal,
                                      itemCount: entry.value.length,
                                      itemBuilder: (ctx, idx) => buildVideoCard(
                                        ctx,
                                        entry.value[idx],
                                        itemWidth,
                                        cs,
                                        tt,
                                      ),
                                    ),
                                  ),
                                ),

                                // Left arrow
                                Positioned(
                                  left: 8,
                                  top: 0,
                                  bottom: 0,
                                  child: Center(
                                    child: InkWell(
                                      onTap: () {
                                        final c = _controllers[entry.key]!;
                                        final offset =
                                            c.offset -
                                            (itemWidth + 12) *
                                                2; // scroll two items
                                        c.animateTo(
                                          offset.clamp(
                                            0.0,
                                            c.position.maxScrollExtent,
                                          ),
                                          duration: const Duration(
                                            milliseconds: 300,
                                          ),
                                          curve: Curves.easeOut,
                                        );
                                      },
                                      borderRadius: BorderRadius.circular(30),
                                      child: Container(
                                        width: 36,
                                        height: 72,
                                        decoration: BoxDecoration(
                                          color: Colors.black.withOpacity(0.35),
                                          borderRadius: BorderRadius.circular(
                                            30,
                                          ),
                                        ),
                                        child: const Icon(
                                          Icons.arrow_back_ios_new,
                                          color: Colors.white,
                                          size: 18,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),

                                // Right arrow
                                Positioned(
                                  right: 8,
                                  top: 0,
                                  bottom: 0,
                                  child: Center(
                                    child: InkWell(
                                      onTap: () {
                                        final c = _controllers[entry.key]!;
                                        final offset =
                                            c.offset +
                                            (itemWidth + 12) *
                                                2; // scroll two items
                                        c.animateTo(
                                          offset.clamp(
                                            0.0,
                                            c.position.maxScrollExtent,
                                          ),
                                          duration: const Duration(
                                            milliseconds: 300,
                                          ),
                                          curve: Curves.easeOut,
                                        );
                                      },
                                      borderRadius: BorderRadius.circular(30),
                                      child: Container(
                                        width: 36,
                                        height: 72,
                                        decoration: BoxDecoration(
                                          color: Colors.black.withOpacity(0.35),
                                          borderRadius: BorderRadius.circular(
                                            30,
                                          ),
                                        ),
                                        child: const Icon(
                                          Icons.arrow_forward_ios,
                                          color: Colors.white,
                                          size: 18,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                SliverToBoxAdapter(child: SizedBox(height: 32)),
              ],
            );
          },
        ),
      ),
    );
  }
}
