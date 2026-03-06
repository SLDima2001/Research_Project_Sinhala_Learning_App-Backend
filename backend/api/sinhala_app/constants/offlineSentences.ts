/**
 * Offline Sentences for Sinhala Learning App
 * Easy sentences for 7-12 year olds (used when backend is unavailable)
 */

export interface OfflineSentence {
    id: string;
    text: string;
    words: string[];
    translation: string;
    difficulty: 'easy';
}

export const OFFLINE_SENTENCES: OfflineSentence[] = [
    {
        id: 'offline_001',
        text: 'මම ළමයෙක්',
        words: ['මම', 'ළමයෙක්'],
        translation: 'I am a child',
        difficulty: 'easy',
    },
    {
        id: 'offline_002',
        text: 'මගේ නම රාජ්',
        words: ['මගේ', 'නම', 'රාජ්'],
        translation: 'My name is Raj',
        difficulty: 'easy',
    },
    {
        id: 'offline_003',
        text: 'මම ඉස්කෝලේට යනවා',
        words: ['මම', 'ඉස්කෝලේට', 'යනවා'],
        translation: 'I go to school',
        difficulty: 'easy',
    },
    {
        id: 'offline_004',
        text: 'මට පොත් ආසයි',
        words: ['මට', 'පොත්', 'ආසයි'],
        translation: 'I like books',
        difficulty: 'easy',
    },
    {
        id: 'offline_005',
        text: 'අම්මා කෑම හදනවා',
        words: ['අම්මා', 'කෑම', 'හදනවා'],
        translation: 'Mother cooks food',
        difficulty: 'easy',
    },
    {
        id: 'offline_006',
        text: 'තාත්තා වැඩට යනවා',
        words: ['තාත්තා', 'වැඩට', 'යනවා'],
        translation: 'Father goes to work',
        difficulty: 'easy',
    },
    {
        id: 'offline_007',
        text: 'මල් ලස්සනයි',
        words: ['මල්', 'ලස්සනයි'],
        translation: 'Flowers are beautiful',
        difficulty: 'easy',
    },
    {
        id: 'offline_008',
        text: 'බල්ලා දුවනවා',
        words: ['බල්ලා', 'දුවනවා'],
        translation: 'The dog runs',
        difficulty: 'easy',
    },
    {
        id: 'offline_009',
        text: 'මම වතුර බොනවා',
        words: ['මම', 'වතුර', 'බොනවා'],
        translation: 'I drink water',
        difficulty: 'easy',
    },
    {
        id: 'offline_010',
        text: 'සූර්යයා දිලෙනවා',
        words: ['සූර්යයා', 'දිලෙනවා'],
        translation: 'The sun shines',
        difficulty: 'easy',
    },
    {
        id: 'offline_011',
        text: 'මම ගෙදර යනවා',
        words: ['මම', 'ගෙදර', 'යනවා'],
        translation: 'I go home',
        difficulty: 'easy',
    },
    {
        id: 'offline_012',
        text: 'කුරුල්ලෝ ගී කියනවා',
        words: ['කුරුල්ලෝ', 'ගී', 'කියනවා'],
        translation: 'Birds sing',
        difficulty: 'easy',
    },
];
